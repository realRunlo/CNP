import ansible_runner
r = ansible_runner.run(private_data_dir='/ansible', playbook='../playbook.yml')
print("{}: {}".format(r.status, r.rc))

