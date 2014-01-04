highstate_run:
  cmd.state.highstate:
    - tgt: {{ data['id'] }}
  cmd.saltutil.sync_modules:
    - tgt: {{ data['id'] }}
