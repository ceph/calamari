highstate_run:
  cmd.state.highstate:
    - tgt: {{ data['id'] }}
  cmd.saltutil.syncmodules:
    - tgt: {{ data['id'] }}
