# NOTE:
# TemplaterX intentionally does NOT support modifying DOCX core properties
# (author, title, subject, etc.), even though docxtpl exposes this capability.
#
# This decision was made due to an unresolved issue that causes the generated
# document to trigger a "corrupted document" warning when opened in Word or
# LibreOffice.
#
# The issue occurs simply by accessing existing core properties, for example:
#
#     initial = getattr(self.docx.core_properties, prop)
#
# This operation duplicates the docProps/core.xml part internally, leading to
# document integrity warnings. While this is not a fatal error, it significantly
# degrades usability and user trust in the generated documents.
#
# According to the docxtpl author, this appears to be a python-docx bug rather
# than a docxtpl issue, and it has been open since 2024:
# https://github.com/elapouya/python-docx-template/issues/558
#
# Until this issue is resolved upstream, TemplaterX avoids touching DOCX core
# properties to ensure document integrity and a warning-free user experience.
