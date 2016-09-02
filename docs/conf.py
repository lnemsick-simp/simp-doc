# -*- coding: utf-8 -*-
#
# SIMP documentation build configuration file, created by
# sphinx-quickstart on Tue May 26 11:09:13 2015.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

from __future__ import print_function
import sys
import os
import shlex
import shutil
import datetime
import yaml
import urllib2
import textwrap
import re

on_rtd = os.environ.get('READTHEDOCS') == 'True'

# Pre-Build Manipulation Code

basedir = os.path.abspath(os.getcwd())
github_base = 'https://raw.githubusercontent.com/simp'

changelog_name = 'Changelog.rst'
changelog = os.path.join(basedir, '..', '..', '..',  changelog_name)

os_ver_mapper_name = 'release_mappings.yaml'
os_ver_mapper = os.path.join(basedir, '..', '..', '..', 'build', os_ver_mapper_name)

target_dirs = [ 'dynamic' ]

# Allow this to be built up over time
epilog = []

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '0.0'

# The full version, including alpha/beta/rc tags.
release = 'NEED_FULL_SIMP_BUILD_TREE'

el_major_version = 'UNKNOWN'
el_minor_version = 'MAPPING'

# Grab the version information out of all of the surrounding infrastructure
# files if they exist.

os_ver_mapper_content = None

# This ordering matches our usual default fallback branch scheme
# Need to fix this to go figure out the branches from GitHub directly
github_version_targets = [
    '5.1.X',
    '4.2.X',
    'master'
]

# If we're running on ReadTheDocs, we should go fetch the content from the
# actual branch that we're using
if on_rtd:
    github_version_targets.insert(0,os.environ.get('READTHEDOCS_VERSION'))

# This should be fixed once we move back to the master branch for all mainline
# work.
if not on_rtd or (os.environ.get('READTHEDOCS_VERSION') == 'master'):
    # Attempt to read auto-generated release file. Needs to be run after
    # rake munge:prep
    rel_file = os.path.join(basedir, '..', 'build/rpm_metadata/release')
    if os.path.isfile(rel_file):
        with open(rel_file,'r') as f:
            for line in f:
                _tmp = line.split(':')
            if 'version' in _tmp:
                version = _tmp[-1].strip()
            elif 'release' in _tmp:
                release = _tmp[-1].strip()
    # If we couldn't find that, go ahead and dig through GitHub directly with
    # our best guess.
    else:
        os_simp_spec_urls = []
        for version_target in github_version_targets:
            os_simp_spec_urls.append('/'.join([github_base, 'simp-core', version_target, 'src', 'build', 'simp.spec']))

        # Grab it from the Internet!
        for os_simp_spec_url in os_simp_spec_urls:
            try:
                print("NOTICE: Downloading SIMP Spec File: " + os_simp_spec_url, file=sys.stderr)
                os_simp_spec_content = urllib2.urlopen(os_simp_spec_url).read().splitlines()

                # Read the version out of the spec file and run with it.
                for line in os_simp_spec_content:
                    _tmp = line.split()
                    if 'Version:' in _tmp:
                        version_list = _tmp[-1].split('.')
                        version = '.'.join(version_list[0:2]).strip()
                        version = re.sub('%\{.*?\}', '', version)
                    elif 'Release:' in _tmp:
                        release = _tmp[-1].strip()
                        release = re.sub('%\{.*?\}', '', release)
                break
            except urllib2.URLError:
                next


full_version = "-".join([version, release])
version_family = re.sub('\.\d$',".X",version)

if on_rtd:
    _insert_target = 1
else:
    _insert_target = 0

# Update the github list with the rest of our 'best guess' content
# This is in reverse order so that it's easier to insert
github_version_targets.insert(_insert_target, version_family)
github_version_targets.insert(_insert_target,'simp-' + version_family)

# If we have some sort of valid release, shove it on the stack too.
if release != 'NEED_FULL_SIMP_BUILD_TREE':
    github_version_targets.insert(0,full_version)

if os.path.isfile(os_ver_mapper):
    with open(os_ver_mapper, 'r') as f:
        os_ver_mapper_content = f.read()
else:
    os_ver_mapper_urls = []
    for version_target in github_version_targets:
        os_ver_mapper_urls.append('/'.join([github_base, 'simp-core', version_target, 'build', os_ver_mapper_name]))

    # Grab it from the Internet!
    for os_ver_mapper_url in os_ver_mapper_urls:
        try:
            print("NOTICE: Downloading Version Mapper: " + os_ver_mapper_url, file=sys.stderr)
            os_ver_mapper_content = urllib2.urlopen(os_ver_mapper_url).read()
            # If we don't have a valid version from the RPM spec file, just
            # pick up what we found.
            if version == '0.0':
                version = version_target
            break
        except urllib2.URLError:
            next

release_mapping_list = ['Release Mapping Entry Not Found for Version ' + full_version]

if os_ver_mapper_content != None:
    os_flavors = None
    ver_map = yaml.load(os_ver_mapper_content)
    if version in ver_map['simp_releases']:
        os_flavors = ver_map['simp_releases'][version]['flavors']
    elif version_family in ver_map['simp_releases']:
        os_flavors = ver_map['simp_releases'][version_family]['flavors']

    # Extract the actual OS version supported for placement in the docs
    if os_flavors is not None:
        if os_flavors['RedHat']:
            ver_list = os_flavors['RedHat']['os_version'].split('.')
            el_major_version = ver_list[0]
            el_minor_version = ver_list[1]
        elif os_flavors['CentOS']:
            ver_list = os_flavors['CentOS']['os_version'].split('.')
            el_major_version = ver_list[0]
            el_minor_version = ver_list[1]

        # Build the Release mapping table for insertion into the docs
        release_mapping_list = []
        for os_flavor in os_flavors:
            release_mapping_list.append('* **' + os_flavor + ' ' + os_flavors[os_flavor]['os_version'] + '**')
            for i, iso in enumerate(os_flavors[os_flavor]['isos']):
                release_mapping_list.append("\n   * **ISO #" + str(i+1) + ":** " + iso['name'])
                release_mapping_list.append("   * **Checksum:** " + iso['checksum'])

        # Trailing newline
        release_mapping_list.append('')

epilog.append('.. |simp_version| replace:: %s' % full_version)

el_version = ".".join([el_major_version, el_minor_version])
epilog.append('.. |el_version| replace:: %s' % el_version)

known_os_compat_content = """
Known OS Compatibility
----------------------

{0}
""".format("\n".join(release_mapping_list))

changelog_urls = []
for version_target in github_version_targets:
    changelog_urls.append('/'.join([github_base, 'simp-core', version_target, changelog_name]))

changelog_stub = """
Changelog Stub
==============

.. warning::
    The build scripts could not find a valid Changelog either locally or on the Internet!

.. note::
    Please check your Internet connectivity as well as your local build system.

Attempted Locations:
{0}
""".format("\n".join(["  * %s" % x for x in [changelog] + changelog_urls]))

current_changelog = changelog_stub

for target_dir in target_dirs:
    target_dir = os.path.join(basedir, target_dir)
    if not os.path.exists(target_dir):
            os.mkdir(target_dir)

    changelog_dest =  os.path.join(target_dir, changelog_name)
    known_os_compat_dest =  os.path.join(target_dir, 'Known_OS_Compatibility.rst')

    if os.path.isfile(changelog):
        # Is the Changelog on disk?
        with open(changelog, 'r') as changelog_content:
            current_changelog = changelog_content.read()
    else:
        # Grab it from the Internet!
        # This is really designed for use with ReadTheDocs

        for changelog_url in changelog_urls:
            try:
                print("NOTICE: Downloading Changelog: " + changelog_url, file=sys.stderr)
                current_changelog = urllib2.urlopen(changelog_url).read()
                break
            except urllib2.URLError:
                next

    # Write out the new Changelog
    if current_changelog == changelog_stub:
        sys.stderr.write("Warning: Could not find a valid Changelog, using the stub....\n")

    with open(changelog_dest, 'w') as f:
        f.write(current_changelog)

    with open(known_os_compat_dest, 'w') as f:
        f.write(known_os_compat_content)


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    # To use this, you need to make the necessary variable available in setup
    # using the 'add_config_value' function.
    #
    # Example:
    #   def setup(app):
    #     app.add_config_value('releaselevel', '', 'env') # The third value must always be 'env'
    #
    # Usage:
    #   .. ifconfig:: releaselevel in ('alpha', 'beta', 'rc')
    'sphinx.ext.ifconfig',
    'rst2pdf.pdfbuilder'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The encoding of source files.
#source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'SIMP'
copyright = str(datetime.datetime.now().year) + u', THE SIMP TEAM'
author = u'THE SIMP TEAM'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', '**/*.inc']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme_path = ["_themes"]
html_theme      = "sphinx_rtd_theme"

# adds a file for overwriting the default css. We use this for fixing tables
html_context = {
        'css_files': [
            'https://media.readthedocs.org/css/sphinx_rtd_theme.css',
            'https://media.readthedocs.org/css/readthedocs-doc-embed.css',
            '_static/css_overrides.css',
        ],
    }

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "%s %s.%s documentation" % (project, version, release )

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "images/SIMP_Logo.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
#html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'SIMPdoc'

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
# The paper size ('letterpaper' or 'a4paper').
#'papersize': 'letterpaper',

# The font size ('10pt', '11pt' or '12pt').
#'pointsize': '10pt',

# Additional stuff for the LaTeX preamble.
#'preamble': '',

# Latex figure (float) alignment
#'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
  (master_doc, 'SIMP.tex', u'SIMP Documentation',
   u'THE SIMP TEAM', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'simp', u'SIMP Documentation',
     [author], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  (master_doc, 'SIMP', u'SIMP Documentation',
   author, 'SIMP', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False


# Example configuration for intersphinx: refer to the Python standard library.
#intersphinx_mapping = {'https://docs.python.org/': None}

# PDF
pdf_documents = [
    (master_doc, u'SIMP_Documentation',u'SIMP Documentation', u'SIMP'),
]

pdf_language = "en_US"
pdf_fit_background_mode = "scale"
pdf_compressed = True
pdf_stylesheets = ['sphinx','kerning','letter']
pdf_use_toc = True
pdf_use_index = False
pdf_toc_depth = 3

# tag
tags.add('simp_%s' % version.split('.')[0])

rst_epilog = "\n".join(epilog)
