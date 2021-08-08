from pathlib import Path
import subprocess
import sys

from hat.doit import common


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs']


build_dir = Path('build')
src_py_dir = Path('src_py')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')

build_py_dir = build_dir / 'py'
build_docs_dir = build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir])]}


def task_build():
    """Build"""

    def build():
        common.wheel_build(
            src_dir=src_py_dir,
            dst_dir=build_py_dir,
            src_paths=list(common.path_rglob(src_py_dir,
                                             blacklist={'__pycache__'})),
            name='hat-asn1',
            description='Hat ASN.1 parser and encoder',
            url='https://github.com/hat-open/hat-asn1',
            license=common.License.APACHE2,
            packages=['hat'])

    return {'actions': [build]}


def task_check():
    """Check with flake8"""
    return {'actions': [(_run_flake8, [src_py_dir]),
                        (_run_flake8, [pytest_dir])]}


def task_test():
    """Test"""

    def run(args):
        subprocess.run([sys.executable, '-m', 'pytest',
                        '-s', '-p', 'no:cacheprovider',
                        *(args or [])],
                       cwd=str(pytest_dir),
                       check=True)

    return {'actions': [run],
            'pos_arg': 'args'}


def task_docs():
    """Docs"""

    def build():
        common.sphinx_build(common.SphinxOutputType.HTML, docs_dir,
                            build_docs_dir)
        subprocess.run([sys.executable, '-m', 'pdoc',
                        '--html', '--skip-errors', '-f',
                        '-o', str(build_docs_dir / 'py_api'),
                        'hat.asn1'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)

    return {'actions': [build]}


def _run_flake8(path):
    subprocess.run([sys.executable, '-m', 'flake8', str(path)],
                   check=True)
