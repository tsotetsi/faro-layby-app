from frappe import _, throw, db, exceptions
from frappe.contacts.doctype.contact.contact import get_contact_details

from erpnext.selling.doctype.customer.customer import Customer


class FaroCustomCustomer(Customer):
    """
    Custom Class to handle Faro Customer Lay-by's purchases.
    """
    def validate(self):
        self.validate_layby_details()
        return super().validate()

    def on_update(self):
        self.update_customer_can_make_layby()
        return super().on_update()
    
    def validate_layby_details(self):
        if self.custom_id_or_pp_number is None or self.custom_id_or_pp_number == "":
            if self.custom_form_of_identification == "Identification Document(ID)":
                throw(
                    _(
                        "ID number was not added in 'ID or PP Number' input field."
                    ),
                    title=_("Identification number missing.")
                )
        elif self.custom_form_of_identification == "" or self.custom_form_of_identification is None:
            if self.custom_id_or_pp_number != "" or self.custom_id_or_pp_number is not None:
                throw(
                    _(
                        "Please pick the correct 'Form Of Identification' on the drop down field."
                    ),
                    title="Form of Identification drop-down not set."
                )
        if self.custom_form_of_identification == "Passport Document(PPN)":
            if self.custom_id_or_pp_number == "" or self.custom_id_or_pp_number is None:
                throw(
                    _(
                        "Passport Number was not added in 'ID or PP Number' input field."
                    ),
                    title="Passport Number not populated."
                )
            if self.custom_passport_country_of_origin == "" or self.custom_passport_country_of_origin is None:
                throw(
                    _(
                        "Passport Country of Origin drop-down was not selected."
                    ),
                    title="Passport Country of Origin not set."
                )
    
    def update_customer_can_make_layby(self):
        """
        Updates customer can make lay-by's checkbox based on whether
        they added their phone number, ID or Passport numbers.
        """
        if self.customer_primary_contact:
            # We need to check for None in-case we are adding a new customer.
            # otherwise get_contact_details will throw a DoesNotExistError.
            primary_contact = get_contact_details(self.customer_primary_contact)
            if primary_contact is not None:
                if primary_contact["contact_phone"] != "" and primary_contact["contact_phone"] != None:
                    if self.custom_id_or_pp_number != "" and self.custom_id_or_pp_number != None:
                        db.set_value("Customer", self.name,"custom_is_able_to_make_layby", 1)
                        return self.reload()
                if self.custom_id_or_pp_number == "" or self.custom_id_or_pp_number is None:
                    db.set_value("Customer", self.name,"custom_is_able_to_make_layby", 0)
                    return self.reload()
