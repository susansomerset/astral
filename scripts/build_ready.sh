#!/bin/bash
# build_ready.sh - Build resume or cover letter from Ready directory files
# Usage: ./build_ready.sh <company> <jobid> <type> [open]
# Example: ./build_ready.sh twinhealth 5673498004 resume
#          ./build_ready.sh twinhealth 5673498004 cover open

if [ -z "$1" ] || [ -z "$2" ] || [ -z "$3" ]; then
    echo "Usage: ./build_ready.sh <company> <jobid> <type> [open]"
    echo "  type: 'resume' or 'cover'"
    echo "Example: ./build_ready.sh twinhealth 5673498004 resume"
    echo "         ./build_ready.sh twinhealth 5673498004 cover open"
    exit 1
fi

COMPANY="$1"
JOBID="$2"
TYPE="$3"
OPEN_BROWSER="$4"

# Get script directory (where this script is located)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ASTRAL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
READY_DIR="$ASTRAL_DIR/data/postings/Yup/Ready"
JOB_DIR="$READY_DIR/${COMPANY}_${JOBID}"

# Check if job directory exists
if [ ! -d "$JOB_DIR" ]; then
    echo "❌ Error: Directory not found: $JOB_DIR"
    exit 1
fi

# Set paths based on type
if [ "$TYPE" == "resume" ]; then
    CONTENT_FILE="$JOB_DIR/resume_${COMPANY}_${JOBID}.txt"
    BUILD_SCRIPT="/Users/susansomerset/chuckles/ResumeSite/build_resume.sh"
elif [ "$TYPE" == "cover" ]; then
    CONTENT_FILE="$JOB_DIR/cover_${COMPANY}_${JOBID}.txt"
    BUILD_SCRIPT="/Users/susansomerset/chuckles/ResumeSite/build_cover.sh"
else
    echo "❌ Error: Type must be 'resume' or 'cover'"
    exit 1
fi

# Check if content file exists
if [ ! -f "$CONTENT_FILE" ]; then
    echo "❌ Error: File not found: $CONTENT_FILE"
    exit 1
fi

# Check if build script exists
if [ ! -f "$BUILD_SCRIPT" ]; then
    echo "❌ Error: Build script not found: $BUILD_SCRIPT"
    exit 1
fi

# Change to ResumeSite directory (where the .ps files are located)
RESUMESITE_DIR="/Users/susansomerset/chuckles/ResumeSite"
if [ ! -d "$RESUMESITE_DIR" ]; then
    echo "❌ Error: ResumeSite directory not found: $RESUMESITE_DIR"
    exit 1
fi
cd "$RESUMESITE_DIR" || exit 1

# Determine output file names based on type
if [ "$TYPE" == "resume" ]; then
    OUTPUT_FILE="somerset_resume.html"
elif [ "$TYPE" == "cover" ]; then
    OUTPUT_FILE="coverletter.html"
fi

# Run the build script (pass absolute path to content file)
# We'll handle opening the browser ourselves after moving the file
echo "🔨 Building $TYPE from $CONTENT_FILE..."
"$BUILD_SCRIPT" "$CONTENT_FILE"
BUILD_SUCCESS=$?

# Move HTML file to job directory if build succeeded
if [ $BUILD_SUCCESS -eq 0 ] && [ -f "$RESUMESITE_DIR/$OUTPUT_FILE" ]; then
    mv "$RESUMESITE_DIR/$OUTPUT_FILE" "$JOB_DIR/$OUTPUT_FILE"
    echo "📦 Moved $OUTPUT_FILE to job directory"
    
    # Copy CSS file(s) to job directory (HTML references styles07.css)
    if [ -f "$RESUMESITE_DIR/styles07.css" ]; then
        cp "$RESUMESITE_DIR/styles07.css" "$JOB_DIR/styles07.css"
        echo "📦 Copied styles07.css to job directory"
    fi
    
    # Open browser from job directory if requested
    if [ -n "$OPEN_BROWSER" ] && [ "$OPEN_BROWSER" == "open" ]; then
        echo "🌐 Opening in browser..."
        cd "$JOB_DIR" || exit 1
        open "$OUTPUT_FILE"
    fi
elif [ $BUILD_SUCCESS -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

