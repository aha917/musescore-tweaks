#!/usr/bin/env fish

set -x MUSESAMPLER_INSTRUMENT_FOLDER "/home/$USER/Muse Sounds"
set APP ~/AppImages/musescore_studio_4.7_portable.appimage
mkdir -p exports/pdf exports/mxml

for f in *.mscz
    set base (string replace -r '\.mscz$' '' $f)
    set job (mktemp)
    printf '[{"in":"%s","out":["exports/pdf/%s.pdf","exports/mxml/%s.musicxml",["exports/pdf/%s_",".pdf"]]}]' \
        $f $base $base $base > $job
    $APP -j $job
    rm $job
end
