highstate_run:
  cmd.state.highstate:
    - tgt: {{ data['id'] }}

sync_modules:
  cmd.saltutil.sync_modules:
    - tgt: {{ data['id'] }}
