#!/usr/bin/env python3
#
# Builds the Zowe Conformance docs into pdfs
#
# Copyright this project and it's contributors
# SPDX-License-Identifier: Apache-2.0
#

from markdown import markdown
from weasyprint import HTML, CSS
import logging
import shutil
import os
from pathlib import Path
from datetime import datetime, UTC

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

INPUT_DIR = Path("docs")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

logger.info("Input dir: %s", INPUT_DIR)
logger.info("Output dir: %s", OUTPUT_DIR)

RELEASE_TAG = os.getenv("GITHUB_REF_NAME", "dev")
BUILD_DATE = datetime.now(UTC).strftime("%Y-%m-%d")

logger.info("Release tag: %s", RELEASE_TAG)
logger.info("Build date: %s", BUILD_DATE)

logger = logging.getLogger(__name__)

docs = [
        {'input': 'brand_guidelines.pdf', 'output': 'Zowe.Conformance.Program.-.Brand.Guidelines.pdf'},
        {'input': 'participation_form.md', 'output': 'Zowe.Conformance.Program.-.Participation.Form.pdf'},
        {'input': 'support_provider_evaluation_guide_table.md', 'output': 'Zowe.Support.Provider.-.Test.Evaluation.Guide.Table.pdf', 'wide': True},
        {'input': 'terms_and_conditions.md', 'output': 'Zowe.Conformance.Program.-.Terms.and.Conditions.pdf'},
        {'input': 'test_evaluation_guide_table.md', 'output': 'Zowe.Conformance.Program.-.Test.Evaluation.Guide.Table.pdf', 'wide': True},
        ]

for doc in docs:
    sourcewithpath = INPUT_DIR / doc.get('input')
    outputwithpath = OUTPUT_DIR / doc.get('output')

    logger.info(f"Reading {sourcewithpath}")
    
    _, ext = os.path.splitext(doc.get('input'))
    ext = ext.lower()  # normalize to lowercase

    if ext == ".pdf":
        shutil.copyfile(sourcewithpath, outputwithpath)
    elif ext == ".md":
        md = open(sourcewithpath).read()
        html_body = markdown(
            md,
            extensions=[
                "tables",
                "fenced_code",
                "attr_list",
                "toc",
            ],
            extension_configs={
                "toc": {
                    "permalink": False,
                    "toc_depth": "2-6",
                    "slugify": lambda s, sep: s.lower().replace(" ", sep),
                }
            }
        )

        styles = ''
        if doc.get('wide'):
            logger.info("Printing landscape")
            styles = '@page { size: A4 landscape; }' 
        
        HTML(string=f"""
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8">
          <style>
            @page {{
               @bottom-center {{
                  content: "Version {{RELEASE_TAG}} — Generated {{BUILD_DATE}}";
                  font-size: 9pt;
                  color: #555;
               }}
            }}
            {styles}
          </style>
        </head>
        <body>
        {html_body}
        </body>
        </html>
        """).write_pdf(outputwithpath)
    else:
        logger.error(f"Invalid file {sourcewithpath}")
        continue

    logger.info(f"Wrote {outputwithpath}")

