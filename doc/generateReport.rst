Generate a Report
=================

Generating the Report
---------------------

Click the `Generate` button or use the shortcut key `^+g`.

If any section is missing a plugin, it will be excluded from the report.
Otherwise, the section will be inserted according to its cardinality in the
section list. If a plugin lacks information necessary to generate, the plugin
developer `should` have made the plugin to ask the user at generation time. If
the plugin is unable to generate text, generation will stop.

Exporting the Generated Document
--------------------------------

Click the `Export` menu-button to open the the export menu. From this menu,
select a file format to export to. Note that .odt and .docx exporting requires
pypandoc to be installed. This should already be done if the installation
instructions were followed (but it isn't strictly necessary.)