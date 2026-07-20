```bash
scp -r ./custom_components/ root@192.168.1.99:/homeassistant/custom_components/
```

## Updating the pyhOn dependency

`requirements` in `manifest.json` points at `pyhOn @ git+https://github.com/KDunin/pyhOn.git@main`.
Home Assistant only reinstalls a requirement when its string changes, so bumping code on the
`main` branch of pyhOn does **not** get picked up automatically — the package must be
force-reinstalled and core restarted after every pyhOn change:

```bash
ssh root@192.168.1.99 '\
  docker exec homeassistant pip install --force-reinstall --no-deps \
    "git+https://github.com/KDunin/pyhOn.git@main" && \
  ha core restart'
```

Combine both steps into one deploy:

```bash
scp -r ./custom_components/ root@192.168.1.99:/homeassistant/custom_components/ && \
ssh root@192.168.1.99 '\
  docker exec homeassistant pip install --force-reinstall --no-deps \
    "git+https://github.com/KDunin/pyhOn.git@main" && \
  ha core restart'
```
