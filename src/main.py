import ansible_runner
r = ansible_runner.run(private_data_dir='../Deployment/', playbook='../Deployment/playbook.yml')

print("{}: {}".format(r.status, r.rc))

