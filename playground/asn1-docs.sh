#!/bin/sh

. $(dirname -- "$0")/env.sh

exec $PYTHON - "$@" << EOF
import pathlib
import sys
import hat.asn1

repo = hat.asn1.create_repository(*(pathlib.Path(i) for i in sys.argv[1:]))
print(hat.asn1.generate_html_doc(repo))
EOF
