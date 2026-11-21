# Bundled P1GL subset

Source: https://github.com/ppporch/P1GL, snapshot from commit c016bac.
The point, line, native/vector text and retained-frame modules are included,
with the generated font and its original notice. Code is MIT (see LICENSE in this directory);
font data use the separate terms in fonts/HERSHEY-NOTICE.txt.

gline.am1 includes the same short-vector fast path being developed in P1GL:
if both components are at most 127, emit the existing point + native-vector
sequence directly. Long lines retain the prior segmented path. Zero-length
lines retain point-only behavior. Library regression tests check the unchanged
command geometry; Orbit's tests check its full ring scene and status captions.
The complete P1GL frame ownership, clipping and capacity rules still apply.

The bundled frame module supports optional P1GL_DISPLAY_ENTRY and
P1GL_POLL_HOOK. Orbit uses a bank-1 PENMENU wrapper before each retained
scene and polls/resumes light-pen pauses while waiting for completion. The
main loop invokes the menu only after drawing stops. The wrapper override
is for this retained-only application; it is not an immediate-drawing mode.
