#!/usr/bin/env python

"""
CUDA Library Installer

Installs the latest CUDA library supported by CuPy.
"""

# This script will also be used as a standalone script when building wheels.
# Keep the script runnable without CuPy dependency.

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request


_cudnn_records = []
_cutensor_records = []
_nccl_records = []
library_records = {}


def _make_cudnn_url(public_version, filename):
    # https://developer.download.nvidia.com/compute/redist/cudnn/v8.0.2/cudnn-11.0-linux-x64-v8.0.2.39.tgz
    return (
        'https://developer.download.nvidia.com/compute/redist/cudnn' +
        '/v{}/{}'.format(public_version, filename))


def _make_cudnn_record(
        cuda_version, public_version, filename_linux, filename_windows):
    major_version = public_version.split('.')[0]

    if major_version == '7':
        suffix_list = ['']
    elif major_version == '8':
        # Dependency order is documented at:
        # https://docs.nvidia.com/deeplearning/cudnn/api/index.html
        suffix_list = ['', '_ops_infer', '_ops_train',
                       '_cnn_infer', '_cnn_train',
                       '_adv_infer', '_adv_train']
    else:
        raise AssertionError

    return {
        'cuda': cuda_version,
        'cudnn': public_version,
        'assets': {
            'Linux': {
                'url': _make_cudnn_url(public_version, filename_linux),
                'filenames': [f'libcudnn{suffix}.so.{public_version}'
                              for suffix in suffix_list]
            },
            'Windows': {
                'url': _make_cudnn_url(public_version, filename_windows),
                'filenames': [f'cudnn{suffix}64_{major_version}.dll'
                              for suffix in suffix_list]
            },
        }
    }


# Latest cuDNN versions: https://developer.nvidia.com/rdp/cudnn-download
_cudnn_records.append(_make_cudnn_record(
    '11.5', '8.2.4',
    'cudnn-11.4-linux-x64-v8.2.4.15.tgz',
    'cudnn-11.4-windows-x64-v8.2.4.15.zip'))
_cudnn_records.append(_make_cudnn_record(
    '11.4', '8.2.4',
    'cudnn-11.4-linux-x64-v8.2.4.15.tgz',
    'cudnn-11.4-windows-x64-v8.2.4.15.zip'))
_cudnn_records.append(_make_cudnn_record(
    '11.3', '8.2.4',
    'cudnn-11.4-linux-x64-v8.2.4.15.tgz',
    'cudnn-11.4-windows-x64-v8.2.4.15.zip'))
_cudnn_records.append(_make_cudnn_record(
    '11.2', '8.2.4',
    'cudnn-11.4-linux-x64-v8.2.4.15.tgz',
    'cudnn-11.4-windows-x64-v8.2.4.15.zip'))
_cudnn_records.append(_make_cudnn_record(
    '11.1', '8.2.4',
    'cudnn-11.4-linux-x64-v8.2.4.15.tgz',
    'cudnn-11.4-windows-x64-v8.2.4.15.zip'))
_cudnn_records.append(_make_cudnn_record(
    '11.0', '8.2.4',
    'cudnn-11.4-linux-x64-v8.2.4.15.tgz',
    'cudnn-11.4-windows-x64-v8.2.4.15.zip'))
_cudnn_records.append(_make_cudnn_record(
    '10.2', '8.2.4',
    'cudnn-10.2-linux-x64-v8.2.4.15.tgz',
    'cudnn-10.2-windows10-x64-v8.2.4.15.zip'))
library_records['cudnn'] = _cudnn_records


def _make_cutensor_url(platform, filename):
    # https://developer.download.nvidia.com/compute/cutensor/redist/libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz
    return (
        'https://developer.download.nvidia.com/compute/cutensor/' +
        f'redist/libcutensor/{platform}-x86_64/{filename}')


def _make_cutensor_record(
        cuda_version, public_version, filename_linux, filename_windows):
    return {
        'cuda': cuda_version,
        'cutensor': public_version,
        'assets': {
            'Linux': {
                'url': _make_cutensor_url('linux', filename_linux),
                'filenames': ['libcutensor.so.{}'.format(public_version)],
            },
            'Windows': {
                'url': _make_cutensor_url('windows', filename_windows),
                'filenames': ['cutensor.dll'],
            },
        }
    }


_cutensor_records.append(_make_cutensor_record(
    '11.5', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
_cutensor_records.append(_make_cutensor_record(
    '11.4', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
_cutensor_records.append(_make_cutensor_record(
    '11.3', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
_cutensor_records.append(_make_cutensor_record(
    '11.2', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
_cutensor_records.append(_make_cutensor_record(
    '11.1', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
_cutensor_records.append(_make_cutensor_record(
    '11.0', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
_cutensor_records.append(_make_cutensor_record(
    '10.2', '1.3.3',
    'libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz',
    'libcutensor-windows-x86_64-1.3.3.2-archive.zip'))
library_records['cutensor'] = _cutensor_records


def _make_nccl_url(public_version, filename):
    # https://developer.download.nvidia.com/compute/redist/nccl/v2.8/nccl_2.8.4-1+cuda11.2_x86_64.txz
    return (
        'https://developer.download.nvidia.com/compute/redist/nccl/' +
        'v{}/{}'.format(public_version, filename))


def _make_nccl_record(
        cuda_version, full_version, public_version, filename_linux):
    return {
        'cuda': cuda_version,
        'nccl': full_version,
        'assets': {
            'Linux': {
                'url': _make_nccl_url(public_version, filename_linux),
                'filenames': ['libnccl.so.{}'.format(full_version)],
            },
        },
    }


_nccl_records.append(_make_nccl_record(
    '11.5', '2.11.4', '2.11',
    'nccl_2.11.4-1+cuda11.4_x86_64.txz'))
_nccl_records.append(_make_nccl_record(
    '11.4', '2.11.4', '2.11',
    'nccl_2.11.4-1+cuda11.4_x86_64.txz'))
_nccl_records.append(_make_nccl_record(
    '11.3', '2.9.9', '2.9',
    'nccl_2.9.9-1+cuda11.3_x86_64.txz'))
_nccl_records.append(_make_nccl_record(
    '11.2', '2.8.4', '2.8',
    'nccl_2.8.4-1+cuda11.2_x86_64.txz'))
_nccl_records.append(_make_nccl_record(
    '11.1', '2.8.4', '2.8',
    'nccl_2.8.4-1+cuda11.1_x86_64.txz'))
_nccl_records.append(_make_nccl_record(
    '11.0', '2.11.4', '2.11',
    'nccl_2.11.4-1+cuda11.0_x86_64.txz'))
_nccl_records.append(_make_nccl_record(
    '10.2', '2.11.4', '2.11',
    'nccl_2.11.4-1+cuda10.2_x86_64.txz'))
library_records['nccl'] = _nccl_records


def install_lib(cuda, prefix, library):
    if platform.uname().machine.lower() not in ('x86_64', 'amd64'):
        raise RuntimeError('''
Currently this tool only supports x86_64 architecture.''')
    record = None
    lib_records = library_records
    for record in lib_records[library]:
        if record['cuda'] == cuda:
            break
    else:
        raise RuntimeError('''
The CUDA version specified is not supported.
Should be one of {}.'''.format(str([x['cuda'] for x in lib_records[library]])))
    if prefix is None:
        prefix = os.path.expanduser('~/.cupy/cuda_lib')
    destination = calculate_destination(prefix, cuda, library, record[library])

    if os.path.exists(destination):
        raise RuntimeError('''
The destination directory {} already exists.
Remove the directory first if you want to reinstall.'''.format(destination))

    target_platform = platform.system()
    asset = record['assets'].get(target_platform, None)
    if asset is None:
        raise RuntimeError('''
The current platform ({}) is not supported.'''.format(target_platform))

    print('Installing {} {} for CUDA {} to: {}'.format(
        library, record[library], record['cuda'], destination))

    url = asset['url']
    print('Downloading {}...'.format(url))
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(os.path.join(tmpdir, os.path.basename(url)), 'wb') as f:
            with urllib.request.urlopen(url) as response:
                f.write(response.read())
        print('Extracting...')
        outdir = os.path.join(tmpdir, 'extract')
        try:
            shutil.unpack_archive(f.name, outdir)
        except shutil.ReadError:
            print('The archive format is not supported in your Python '
                  'environment. Falling back to "tar" command...')
            try:
                os.makedirs(outdir, exist_ok=True)
                subprocess.run(['tar', 'xf', f.name, '-C', outdir], check=True)
            except subprocess.CalledProcessError:
                msg = 'Failed to extract the archive using "tar" command.'
                raise RuntimeError(msg)
        print('Installing...')
        if library == 'cudnn':
            shutil.move(os.path.join(outdir, 'cuda'), destination)
        elif library == 'cutensor':
            if cuda.startswith('11.') and cuda != '11.0':
                cuda = '11'
            if target_platform == 'Linux':
                ext = '.tar.xz'
            elif target_platform == 'Windows':
                ext = '.zip'
            else:
                assert False
            assert url.endswith(ext)
            dir_name = os.path.basename(url)[:-len(ext)]
            license = 'LICENSE'
            shutil.move(
                os.path.join(outdir, dir_name, 'include'),
                os.path.join(destination, 'include'))
            shutil.move(
                os.path.join(outdir, dir_name, 'lib', cuda),
                os.path.join(destination, 'lib'))
            shutil.move(
                os.path.join(outdir, dir_name, license), destination)
        elif library == 'nccl':
            subdir = os.listdir(outdir)  # ['nccl_2.8.4-1+cuda11.2_x86_64']
            assert len(subdir) == 1
            shutil.move(os.path.join(outdir, subdir[0]), destination)
        else:
            assert False
        print('Cleaning up...')
    print('Done!')


def calculate_destination(prefix, cuda, lib, lib_ver):
    """Calculates the installation directory.

    ~/.cupy/cuda_lib/{cuda_version}/{library_name}/{library_version}
    """
    return os.path.join(prefix, cuda, lib, lib_ver)


def main(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--library',
                        choices=['cudnn', 'cutensor', 'nccl'],
                        required=True,
                        help='Library to install')
    parser.add_argument('--cuda', type=str, required=True,
                        help='CUDA version')
    parser.add_argument('--prefix', type=str, default=None,
                        help='Install destination')
    parser.add_argument('--action', choices=['install', 'dump'],
                        default='install',
                        help='Action to perform')
    params = parser.parse_args(args)

    if params.prefix is not None:
        params.prefix = os.path.abspath(params.prefix)

    if params.action == 'install':
        install_lib(params.cuda, params.prefix, params.library)
    elif params.action == 'dump':
        print(json.dumps(library_records[params.library], indent=4))
    else:
        assert False


if __name__ == '__main__':
    main(sys.argv[1:])
