"""Native cache-only Authenticode verification; no PowerShell module dependency.

Windows verifies the PE digest, trusted chain, signing usage and timestamp.
Whole-chain revocation is mandatory and cache-only: missing revocation data is
a blocker, never a reason to omit revocation checks. No trust-store mutation.
Primary contracts:
https://learn.microsoft.com/windows/win32/api/wintrust/nf-wintrust-winverifytrust
https://learn.microsoft.com/windows/win32/api/wintrust/ns-wintrust-wintrust_data
https://learn.microsoft.com/windows/win32/api/wintrust/nf-wintrust-wthelpergetprovsignerfromchain

This in-process API has no invented 30-second deadline. Cache-only/no-UI avoids
online retrieval; actual EXE smoke has an independent hard process timeout.
"""
from __future__ import annotations
import ctypes as C
from pathlib import Path
import sys
import uuid
from cryptography import x509
from cryptography.x509.oid import NameOID

D = C.c_uint32
P = C.c_void_p


class NativeSignatureError(RuntimeError):
    pass


class GUID(C.Structure):
    _fields_ = [('data1', D), ('data2', C.c_uint16), ('data3', C.c_uint16), ('data4', C.c_ubyte * 8)]


class FileInfo(C.Structure):
    _fields_ = [('size', D), ('path', C.c_wchar_p), ('file', P), ('subject', P)]


class TrustData(C.Structure):
    _fields_ = [('size', D), ('policy', P), ('sip', P), ('ui', D), ('revoke', D), ('choice', D),
               ('file', P), ('action', D), ('state', P), ('url', C.c_wchar_p),
               ('flags', D), ('context', D), ('signature_settings', P)]


class ProviderCertPrefix(C.Structure):
    # Only the documented first two members are read from the full structure.
    _fields_ = [('size', D), ('cert', P)]


class CertContext(C.Structure):
    _fields_ = [('encoding', D), ('encoded', P), ('length', D), ('info', P), ('store', P)]


def trusted_wintrust():
    if sys.platform != 'win32':
        raise NativeSignatureError('SIGNATURE_NATIVE_WINDOWS_REQUIRED')
    kernel = C.WinDLL('kernel32', use_last_error=True)
    kernel.GetSystemDirectoryW.argtypes = [C.c_wchar_p, D]
    kernel.GetSystemDirectoryW.restype = D
    buffer = C.create_unicode_buffer(32768)
    length = kernel.GetSystemDirectoryW(buffer, len(buffer))
    if not 0 < length < len(buffer):
        raise NativeSignatureError('SIGNATURE_NATIVE_PROVIDER_UNAVAILABLE')
    path = Path(buffer.value) / 'wintrust.dll'
    if not path.is_file() or any(p.is_symlink() or
            (p.exists() and getattr(p.lstat(), 'st_file_attributes', 0) & 0x400) for p in (path, *path.parents)):
        raise NativeSignatureError('SIGNATURE_NATIVE_PROVIDER_UNAVAILABLE')
    win = C.WinDLL(str(path), use_last_error=True)
    # A preloaded module or private bundle directory must not substitute a DLL.
    kernel.GetModuleFileNameW.argtypes = [P, C.c_wchar_p, D]
    kernel.GetModuleFileNameW.restype = D
    actual = C.create_unicode_buffer(32768)
    size = kernel.GetModuleFileNameW(win._handle, actual, len(actual))
    if not 0 < size < len(actual) or Path(actual.value).resolve(strict=True) != path.resolve(strict=True):
        raise NativeSignatureError('SIGNATURE_NATIVE_PROVIDER_UNAVAILABLE')
    win.WinVerifyTrust.argtypes = [P, C.POINTER(GUID), C.POINTER(TrustData)]
    win.WinVerifyTrust.restype = C.c_int32
    win.WTHelperProvDataFromStateData.argtypes = [P]
    win.WTHelperProvDataFromStateData.restype = P
    win.WTHelperGetProvSignerFromChain.argtypes = [P, D, C.c_int, D]
    win.WTHelperGetProvSignerFromChain.restype = P
    win.WTHelperGetProvCertFromChain.argtypes = [P, D]
    win.WTHelperGetProvCertFromChain.restype = C.POINTER(ProviderCertPrefix)
    return win


def verified_signer_der(path: Path) -> tuple[int, bytes | None]:
    win = trusted_wintrust()
    file = FileInfo(C.sizeof(FileInfo), str(path), None, None)
    data = TrustData()
    data.size = C.sizeof(TrustData)
    data.ui = 2  # WTD_UI_NONE, with INVALID_HANDLE_VALUE (no interactive user).
    data.revoke = 1  # WTD_REVOKE_WHOLECHAIN; never WTD_REVOCATION_CHECK_NONE.
    data.choice = 1  # WTD_CHOICE_FILE: verify actual PE bytes, not a manifest.
    data.file = C.addressof(file)
    data.action = 1  # WTD_STATEACTION_VERIFY; state closed in finally.
    data.flags = 0x40 | 0x1000 | 0x2000  # REVOCATION_CHECK_CHAIN | CACHE_ONLY | DISABLE_MD2_MD4.
    action = GUID.from_buffer_copy(uuid.UUID('00aac56b-cd44-11d0-8cc2-00c04fc295ee').bytes_le)
    try:
        code = win.WinVerifyTrust(P(-1), C.byref(action), C.byref(data)) & 0xffffffff
        if code != 0:
            return code, None  # Any nonzero status fails closed; no HRESULT shortcuts.
        provider = win.WTHelperProvDataFromStateData(data.state)
        signer = win.WTHelperGetProvSignerFromChain(provider, 0, False, 0) if provider else None
        certificate = win.WTHelperGetProvCertFromChain(signer, 0) if signer else None
        if not certificate or certificate.contents.size < C.sizeof(ProviderCertPrefix) or not certificate.contents.cert:
            raise NativeSignatureError('SIGNATURE_SIGNER_UNVERIFIED')
        context = C.cast(certificate.contents.cert, C.POINTER(CertContext)).contents
        if not context.encoded or not 0 < context.length <= 2**20:
            raise NativeSignatureError('SIGNATURE_SIGNER_UNVERIFIED')
        return 0, C.string_at(context.encoded, context.length)
    finally:
        data.action = 2  # WTD_STATEACTION_CLOSE, including all failure paths.
        win.WinVerifyTrust(P(-1), C.byref(action), C.byref(data))


def psf_native_signature(path: Path) -> dict:
    try:
        code, der = verified_signer_der(path)
        if code:
            if code == 0x800b0100:
                return {'status': 'NotSigned', 'signer': 'UNVERIFIED'}
            if code == 0x80096010:
                return {'status': 'HashMismatch', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_DIGEST_MISMATCH'}
            if code == 0x800b010c:
                return {'status': 'NotTrusted', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_CERT_REVOKED'}
            if code in {0x80092012, 0x80092013, 0x800b010e}:
                return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_REVOCATION_UNAVAILABLE'}
            return {'status': 'NotTrusted', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_NATIVE_TRUST_UNVERIFIED'}
        if not der:
            raise NativeSignatureError('SIGNATURE_SIGNER_UNVERIFIED')
        certificate = x509.load_der_x509_certificate(der)
        psf = any(attribute.value == 'Python Software Foundation'
                  for oid in (NameOID.COMMON_NAME, NameOID.ORGANIZATION_NAME)
                  for attribute in certificate.subject.get_attributes_for_oid(oid))
        if not psf:
            return {'status': 'Valid', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_SIGNER_UNVERIFIED'}
        return {'status': 'Valid', 'signer': 'Python Software Foundation'}
    except NativeSignatureError as error:
        return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': str(error)}
    except (OSError, ValueError, TypeError, AttributeError):
        return {'status': 'UnknownError', 'signer': 'UNVERIFIED', 'reason': 'SIGNATURE_NATIVE_METADATA_INVALID'}
