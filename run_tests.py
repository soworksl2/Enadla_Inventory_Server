import os
import sys


ROOT_TEST_DIRECTORY = './tests'


def turn_off_echo():
    os.system('echo off')


def turn_on_echo():
    os.system('echo on')


def load_envs():
    # with open('./.env', 'r') as f:
    #     for line in f.readlines():
    #         os.system(f'SET {line}')
    
    with open('./.env', 'r') as f:
        for line in f.readlines():
            key, value = line.split('=')
            os.environ[key] = value


def load_src_to_sys_path():
    current_dir = os.path.dirname(__file__)
    current_dir = os.path.abspath(current_dir)
    src_dir = os.path.join(current_dir, 'src')

    os.system(f'SET PYTHONPATH="{src_dir}"')
    # sys.path.append(src_dir)


def execute_all():
    arguments: str = f'-m unittest discover -s "{ROOT_TEST_DIRECTORY}" -p test_*.py'

    if len(sys.argv) > 2:
        for extra_argument in sys.argv[2:]:
            arguments += f' {extra_argument}'

    os.system(f'python {arguments}')


def execute_custom():
    arguments: str = '-m unittest'

    for extra_argument in sys.argv[2:]:
        arguments += f' {extra_argument}'

    os.system(f'python {arguments}')


if __name__ == '__main__':
    # sys.argv.append('unit')
    # sys.argv.append('-v')
    if len(sys.argv) <= 1:
        print("ERROR: no arguments passed")
        exit(-1)

    option: str = sys.argv[1]

    turn_off_echo()

    # os.system('setlocal')

    load_envs()
    load_src_to_sys_path()

    turn_on_echo()

    match option:
        case 'all':
            execute_all()
        case 'custom':
            execute_custom()
        case _:
            print(f'no option for "{option}"')

    # os.system('endlocal')
