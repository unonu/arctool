Create a Report Profile
=======================

In order for the report to output any content at generation, you will need to
create sections and assign plugins to them.

Adding and Manipulating Sections
--------------------------------

To add a section, click the `Add Section` button or use the shortcut
`^+shift+n`.

Once a section has been created, the section manipulation buttons will become
active. These buttons allow sections to moved up or down or deleted.

In addition to the section manipulation buttons, the section tools will become
available when a section is selected. The section tools allow you to change the
section title, enable/disable section title at generation and assign a plugin 
to the section.

Selecting a Plugin
------------------

In the section tools, click the `Set...` button. The `Plugin Selection Dialog`
should open and display a list of available packages. Select a package and the
second list should populate with the plugin names from that package. Selecting
a plugin will display some basic information about the plugin to the right.

Click `Okay` to assign the plugin to the current section.

Assigning Document Properties
-----------------------------

Not yet supported

Saving and Loading the Profile
------------------------------

After constructing several sections, assigning them plugins and populating
those plugins, you may wish to save the profile for later use. Profiles can be
saved and opened using the profile tools buttons beneath the section list.
Alternatively, the File menu houses these actions in addition to a `Save As`
action. Furthermore, these actions are accessible with the typical shortcut
combinations (`^+s`, `^+shift+s` and `^+o`.)

If a profile is modified and these changes are not yet saved, this will be
indicated in ARCTool's titlebar with an asterisk by the profile name.

Profiles can be opened at runtime by simply passing the profile filepath as a
command line argument:
	`./main.py path/to/profile.arp`