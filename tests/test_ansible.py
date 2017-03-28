import pytest


@pytest.fixture()
def AnsibleDefaults(Ansible):
    return Ansible("include_vars", "defaults/main.yml")["ansible_facts"]


@pytest.fixture()
def AnsibleVars(Ansible):
    return Ansible("include_vars", "tests/group_vars/group01.yml")["ansible_facts"]


@pytest.fixture()
def Hostname(TestinfraBackend):
    return TestinfraBackend.get_hostname()


def test_monit_user(User, Group, AnsibleDefaults):
    assert User(AnsibleDefaults["monit_user"]).exists
    assert Group(AnsibleDefaults["monit_group"]).exists
    assert User(AnsibleDefaults["monit_user"]).group == AnsibleDefaults["monit_group"]


def test_monit_conf(File, User, Group, AnsibleDefaults, Hostname):
    conf_dir = File(AnsibleDefaults["monit_conf_dir"])
    conf_file = File(AnsibleDefaults["monit_conf_dir"] + "/monitrc")
    assert conf_dir.exists
    assert conf_dir.is_directory
    if Hostname == "monit-old":
        assert conf_dir.user == 'root'
        assert conf_dir.group == 'root'
    if Hostname == "monit":
        assert conf_dir.user == AnsibleDefaults["monit_user"]
        assert conf_dir.group == AnsibleDefaults["monit_group"]
    assert conf_file.exists
    assert conf_file.is_file


def test_monit_executable(File, Command, AnsibleDefaults):
    monit = File("/usr/local/bin/monit")
    assert monit.exists
    assert monit.is_file
    assert monit.user == "root"
    monit_version = Command("monit --version")
    assert monit_version.rc is 0
    assert AnsibleDefaults["monit_version"] in monit_version.stdout


def test_monit_service(File, Service, Socket, AnsibleDefaults):
    assert File("/lib/systemd/system/monit.service").exists
