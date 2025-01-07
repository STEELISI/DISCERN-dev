## discern

Researchers across the US use <span style="color:green">cyberinfrastructures</span> to conduct
experimental activities. The research value these infrastructures provide makes them compelling
<span style="color:red">attack targets</span>; attackers may attempt to compromise the
infrastructure and exfiltrate research data, deploy ransomware, or enlist resources into botnets to
send spam, participate in DDOS, or perform cryptomining.

The DISCERN project at the [USC Information Sciences Institute](https://isi.edu) is producing
datasets to capture the behavior of such malicious activities.  Our work focuses on the [SPHERE
testbed](https://sphere-project.net), a novel research infrastructure which provides resources and
services in support of security and privacy research.  Our approach is to conduct <span
style="color:green">controlled malicious activities</span> alongside legitimate activities from
SPHERE users, and to produce datasets that capture those malicious and benign activities. Our goal
is for these datasets to enable novel research into new defenses to better secure the nation's
cyberinfrastructure.

## tools

- [BYOB](https://github.com/STEELISI/byob) - We use BYOB ("Build Your Own Botnet") to construct
  malicious experiments
- [Instrumentation](https://gitlab.com/mergetb/tech/instrumentation) - We are building sensors into
  the Merge testbed platform, which powers the SPHERE research infrastructure. These tools capture
  network metadata, OS metadata, system logs, and user interface activities. Our tools are designed
  for Merge, but are general enough to be deployed on most computational platforms.

## publications and presentations

[2024 CICI PI Meeting](./2024_Brian-Kocoloski_NSF-CICI.pdf) - overview of DISCERN's activities
