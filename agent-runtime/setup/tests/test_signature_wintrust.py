"""Native trust state/signer binding and strict revocation rejection."""
from pathlib import Path
from types import SimpleNamespace
import pytest
from agent_setup import signature_wintrust as signature


@pytest.mark.parametrize('code,reason', [
    (0x800b010c, 'SIGNATURE_CERT_REVOKED'),
    (0x80092013, 'SIGNATURE_REVOCATION_UNAVAILABLE'),
    (0x80092012, 'SIGNATURE_REVOCATION_UNAVAILABLE'),
    (0x800b010e, 'SIGNATURE_REVOCATION_UNAVAILABLE'),
    (0x80096010, 'SIGNATURE_DIGEST_MISMATCH'),
    (0x800b0109, 'SIGNATURE_NATIVE_TRUST_UNVERIFIED'),
    (1, 'SIGNATURE_NATIVE_TRUST_UNVERIFIED'),
])
def test_every_nonzero_trust_result_including_positive_hresult_refuses_psf(monkeypatch, code, reason):
    monkeypatch.setattr(signature, 'verified_signer_der', lambda p: (code, b'not-used'))
    monkeypatch.setattr(signature.x509, 'load_der_x509_certificate', lambda d: pytest.fail('must not inspect untrusted signer'))
    result = signature.psf_native_signature(Path('public-synthetic.dll'))
    assert result['status'] != 'Valid' and result['signer'] == 'UNVERIFIED' and result['reason'] == reason


def test_missing_or_malformed_signer_der_cannot_create_psf_authority(monkeypatch):
    monkeypatch.setattr(signature, 'verified_signer_der', lambda p: (0, None))
    assert signature.psf_native_signature(Path('public.dll'))['reason'] == 'SIGNATURE_SIGNER_UNVERIFIED'
    monkeypatch.setattr(signature, 'verified_signer_der', lambda p: (0, b'not-a-certificate'))
    assert signature.psf_native_signature(Path('public.dll'))['reason'] == 'SIGNATURE_NATIVE_METADATA_INVALID'


def test_same_verified_state_signer_must_be_exact_psf_name(monkeypatch):
    monkeypatch.setattr(signature, 'verified_signer_der', lambda p: (0, b'public-synthetic-der'))
    monkeypatch.setattr(signature.x509, 'load_der_x509_certificate', lambda d:
        SimpleNamespace(subject=SimpleNamespace(get_attributes_for_oid=lambda oid:
            [SimpleNamespace(value='Unrelated Software Foundation')])) )
    result = signature.psf_native_signature(Path('public.dll'))
    assert result['signer'] == 'UNVERIFIED' and result['reason'] == 'SIGNATURE_SIGNER_UNVERIFIED'


def test_native_trust_policy_and_state_close_are_bound_even_when_verification_fails(monkeypatch):
    calls=[]
    def verify(hwnd, action, data):
        value=data._obj
        calls.append(value.action)
        assert value.revoke == 1 and value.flags == (0x40|0x1000|0x2000)
        assert value.ui == 2 and value.choice == 1
        assert not (value.flags & (0x10|0x200))  # No revocation skip or hash-only policy.
        return 1
    monkeypatch.setattr(signature,'trusted_wintrust',lambda:SimpleNamespace(WinVerifyTrust=verify))
    assert signature.verified_signer_der(Path('public.dll')) == (1,None)
    assert calls == [1,2]


def test_signer_extraction_failure_still_closes_windows_trust_state(monkeypatch):
    calls=[]
    def verify(hwnd,action,data):
        calls.append(data._obj.action)
        return 0
    win=SimpleNamespace(WinVerifyTrust=verify,WTHelperProvDataFromStateData=lambda state: None)
    monkeypatch.setattr(signature,'trusted_wintrust',lambda:win)
    with pytest.raises(signature.NativeSignatureError,match='SIGNER_UNVERIFIED'):
        signature.verified_signer_der(Path('public.dll'))
    assert calls == [1,2]
