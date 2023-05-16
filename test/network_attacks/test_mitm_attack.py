import subprocess
from pathlib import Path

import fnfqueue
import pytest
import yaml

from dhalsim.network_attacks.mitm_attack import SyncedAttack, MiTMAttack


@pytest.fixture
def intermediate_yaml_path():
    return Path("test/auxilary_testing_files/intermediate_yaml_network_attacks.yaml")


@pytest.fixture
def yaml_index():
    return 0


@pytest.fixture
def os_mock(mocker):
    mocked_os = mocker.Mock()
    mocked_os.system.return_value = None

    mocker.patch("os.system", mocked_os.system)
    return mocked_os


@pytest.fixture
def subprocess_mock(mocker):
    process = mocker.Mock()
    process.communicate.return_value = None
    process.wait.return_value = None
    process.terminate.return_value = None

    mocker.patch("subprocess.Popen", return_value=process)
    return process


@pytest.fixture
def fnfqueue_mock(mocker, fnfqueue_bound_mock):
    queue = mocker.Mock()
    queue.close.return_value = None
    queue.bind.return_value = fnfqueue_bound_mock

    mocker.patch("fnfqueue.Connection", return_value=queue)
    return queue


@pytest.fixture
def fnfqueue_bound_mock(mocker):
    q = mocker.Mock()
    q.set_mode.return_value = None
    q.unbind.return_value = None

    return q


@pytest.fixture
def launch_arp_poison_mock(mocker):
    return mocker.patch('dhalsim.network_attacks.mitm_attack.launch_arp_poison', return_value=None)


@pytest.fixture
def restore_arp_mock(mocker):
    return mocker.patch('dhalsim.network_attacks.mitm_attack.restore_arp', return_value=None)


@pytest.fixture
def attack(intermediate_yaml_path, yaml_index, mocker):
    #mocker.patch.object(SyncedAttack, 'initialize_db', return_value=None)
    return MiTMAttack(intermediate_yaml_path, yaml_index)


def test_init(intermediate_yaml_path, yaml_index, os_mock, mocker):
    #mocker.patch.object(SyncedAttack, 'initialize_db', return_value=None)
    mitm_attack = MiTMAttack(intermediate_yaml_path, yaml_index)

    assert mitm_attack.yaml_index == yaml_index
    with intermediate_yaml_path.open() as yaml_file:
        data = yaml.load(yaml_file, Loader=yaml.FullLoader)
        assert mitm_attack.intermediate_yaml == data
        assert mitm_attack.intermediate_attack == data['network_attacks'][0]
        assert mitm_attack.intermediate_plc == data['plcs'][1]
    assert mitm_attack.attacker_ip == "192.168.1.4"
    assert mitm_attack.target_plc_ip == "192.168.1.1"
    assert os_mock.system.call_count == 1


def test_setup(os_mock, subprocess_mock, attack, launch_arp_poison_mock, mocker, fnfqueue_mock, fnfqueue_bound_mock):
    attack.setup()

    assert os_mock.system.call_count == 5
    assert launch_arp_poison_mock.call_count == 1
    assert fnfqueue.Connection.call_count == 1
    fnfqueue_mock.bind.assert_called_with(1)
    fnfqueue_bound_mock.set_mode.assert_called_with(fnfqueue.MAX_PAYLOAD, fnfqueue.COPY_PACKET)


def test_interrupt_from_state_1(attack, mocker):
    mocker.patch.object(MiTMAttack, 'teardown', return_value=None)
    attack.state = 1
    attack.interrupt()

    assert attack.teardown.call_count == 1


def test_interrupt_from_state_0(attack, mocker):
    mocker.patch.object(MiTMAttack, 'teardown', return_value=None)
    attack.state = 0
    attack.interrupt()

    assert attack.teardown.call_count == 0

def test_teardown(attack, restore_arp_mock, os_mock, subprocess_mock, mocker):
    attack.teardown()

    assert restore_arp_mock.call_count == 1
    assert os_mock.system.call_count == 4
    assert subprocess_mock.terminate.call_count == 1
