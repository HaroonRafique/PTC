# Files-only ISIS RCS reference snapshot

This snapshot contains only the five direct inputs required for the approved
PyPTC admission recipe. It has no nested Git repository and no other files from
`isis_2024`.

The inputs were materialized from the exact `isis_2024` Git tree at commit
`1bada6a2ab94edd426c52b7e97a5d335926e0646`, not copied from its dirty working
tree. `source_manifest.json` records the authorization, source identity, file
hashes, and checkout state observed at copy time. The complete porcelain-v2
status is retained in `source_checkout_status.porcelain-v2.txt`. The source
checkout was dirty and at another revision; this files-only bundle is therefore
used as an explicitly authorized `working-copy-snapshot`, not called a clean
checkout.

The run recipe uses the files in this snapshot in this order:
`ISIS.injected_beam`, `ISIS.elements`, `ISIS.strength`, `2023.strength`, then
`ISIS.sequence`. It selects `synchrotron`, keeps `a1=b1=0`, sets
`kqtd=kqtf=0`, and permits one MAD-X TWISS reference calculation. Each attempt
must copy and hash this closure into its own immutable run bundle before either
engine runs. Do not edit these source files in place.
