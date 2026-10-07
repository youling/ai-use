import importlib.util
from pathlib import Path
import pytest

s=importlib.util.spec_from_file_location('scan',Path(__file__).parent/'secret_scan.py')
scan=importlib.util.module_from_spec(s);s.loader.exec_module(scan)

def test_parser_marker_is_not_key_material():
    marker=('-----BEGIN '+'PRIVATE KEY-----').encode()
    assert not scan.contains_material(marker+b'\0parser string')
    assert scan.contains_material(marker+b'\n'+b'A'*64+b'\n')
    assert scan.contains_material(marker+b'\r\n'+b'A'*64+b'\r\n')

def test_opaque_token_signature_and_boundary():
    token=('gh'+'s_').encode()+b'A'*40
    assert scan.contains_material(b'prefix'+token+b'suffix')
    assert scan.contains_material((b'x'*4090+token) [-4096:])

def test_public_vector_exception_is_exact_path_and_digest():
    with pytest.raises(ValueError,match='PUBLIC_VECTOR_FILE_DRIFT'):
        scan.verify_public_vectors('foreign/library',b'arbitrary')
    with pytest.raises(ValueError,match='PUBLIC_VECTOR_FILE_DRIFT'):
        scan.verify_public_vectors('usr/lib/x86_64-linux-gnu/libgnutls.so.30.40.3',b'changed binary')
