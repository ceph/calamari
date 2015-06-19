
test:
  cmd.run:
    - user: {{ pillar['username'] }}
    - name: "echo foo > out.txt"
    - cwd: "/tmp/"
