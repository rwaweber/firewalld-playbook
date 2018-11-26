# firewalld-playbook #

Small playbook that uses a custom ipset module to compliment the capabilities
of firewalld.

In my experience, I've ended up using `with_items` over increasingly large
lists on increasingly large sets of infrastructure.

This unfortunately led to an `O(n*m)` performance time for my ansible playbooks
which was less than ideal. Where n is the number of servers having ansible
run on them and m is the number of addresses being iterated over in the
configuration.

Since ansible is designed to scale better across more machines than it is over
playbook diration, a smarter coworker than me hinted at the direction of ipsets
since they were designed to be able to solve this sort of problem with minmal
headache and firewalld already has full support for them!
