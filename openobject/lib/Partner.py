from ooBase import APIbase


class Partner(APIbase):
    """
    Base class for Partners, currently suppliers and customers
    extend this class.
    """

    def __init__(self, name, phone, supplier, customer, id, email=None,
            mobile=None, fax=None,
            property_acct_position="Normal Taxes",
            property_acct_rec="Accounts Receivable",
            property_acct_pay="Accounts Payable",
            property_payment_term="30 Net Days",
            property_product_pricelist="Public Pricelist",
            property_product_pricelist_purchase="Default Purchase Pricelist",
            property_stock_customer="",
            category=None,
            cnx=None):
        """
        We're using customer ID as the ref number

        Test/Example:
        >>> P = Partner("TRPL29", "8778507587", False, False)
        >>> P.address("Blue Springs", "MO", "64015", "2567 SW 90 Hwy", "US")
        >>> P.get_address()
        >>> P.get_invoice_address()

        end Test/Example

        params:
        REQUIRED:
        name: The Customer's full name, string
        phone: The Customer's phone number, string
        supplier: If partner is supplier, boolean
        customer: If partner is customer, boolean
        id: Customer StoreKeeper ID, int


        OPTIONAL:
        email: Customer email, string
        mobile: Customer mobile, string
        fax: Customer fax number, string
        property_acct_position: 
        property_acct_rec: 
        property_acct_pay:
        property_payment_term:
        property_product_pricelist
        property_product_pricelist_purchase
        property_stock_customer
        category=None,

        cnx: a connection object.

        """

        APIbase.__init__(self, cnx)
        self.name = name

        objectName = 'res.partner'

        #search = [('name', '=', name)]
        search = [('ref', '=', id)]

        property_acct_position_id = self._get(
            [("name", "=", property_acct_position)], 'account.fiscal.position')
        property_acct_rec_id = self._get(
            [("name", "=", property_acct_rec)], 'account.account')
        property_acct_pay_id = self._get(
            [("name", "=", property_acct_pay)], 'account.account')

        property_payment_term_id = self._get(
            [("name", "=", property_payment_term)], 'account.payment.term')
        property_product_pricelist_id = self._get(
            [("name", "=", property_product_pricelist)], 'product.pricelist')
        property_product_pricelist_purchase_id = self._get(
            [("name", "=", property_product_pricelist_purchase)],
            'product.pricelist')

        args = {
            'name': name,
            'phone': phone,
            'email': email,
            'mobile': mobile,
            'fax': fax,
            'customer': customer,
            'supplier': supplier,
            'ref': str(id),
            'property_account_position': property_acct_position_id,
            'property_account_receivable': property_acct_rec_id,
            'property_account_payable': property_acct_pay_id,
            'property_payment_term': property_payment_term_id,
            'property_product_pricelist': property_product_pricelist_id,
            'property_product_pricelist_purchase':
                property_product_pricelist_purchase_id,
        }

        if category:
            category_id = self._get([("name", "=", category)],
                'res.partner.category')
            args['category_id'] = [(4, category_id)]

        #update or create pattern
        self.partner_id = self._replace_or_create(search, objectName, args)

    def address(self, city, state, zip, street, country, type="default",
        street2=None):
        """
        adds address to Partners

        Params:
        REQUIRED:
        city: Name of the city, string
        state: state code, two letters, string
        zip: zip code, int
        street: first part of street address, string
        country: country name, I will look up the country_id, string
        type:choose from delivery, default and invoice typically, string

        OPTIONAL:
        street2: second part of street

        """

        country_id = self._get([("name", "=", country)], 'res.country')

        try:
            state_id = self._get([("code", "=", state)], 'res.country.state')
        except:
            state_id = None
            country_id = None

        args = {
            'partner_id': self.partner_id,
            'country_id': country_id,
            'type': type,
            'city': city,
            'state_id': state_id,
            'zip': zip,
            'street': street,
            'street2': street2,
        }

        objName = 'res.partner.address'
        search = [('partner_id', '=', self.partner_id), ('type', '=', type)]

        self.address_id = self._replace_or_create(search, objName, args)

    def get_address(self):
        """
        Returns a delivery or default address, sets self.address_id to be used
        in other object creation
        """
        type = 'delivery'
        search = [('partner_id', '=', self.partner_id), ('type', '=', type)]

        try:
            self.address_id = self._get(search, 'res.partner.address')
        except:
            type = 'default'
            search = [('partner_id', '=', self.partner_id), ('type', '=', type)]
            self.address_id = self._get(search, 'res.partner.address')

    def get_invoice_address(self):
        """
        Returns an invoice or default address
        """
        type = 'invoice'
        search = [('partner_id', '=', self.partner_id), ('type', '=', type)]
        try:
            self.address_id = self._get(search, 'res.partner.address')
        except:
            type = 'default'
            search = [('partner_id', '=', self.partner_id), ('type', '=', type)]
            self.address_id = self._get(search, 'res.partner.address')


class partner_get(Partner):

    def __init__(self, name, cnx=None):
        APIbase.__init__(self, cnx)
        self.partner_id = self._get([("name", "=", name),
            ("active", "=", True)], "res.partner")
        self.get_invoice_address()


class partner_ref_get(Partner):

    def __init__(self, ref, cnx=None):
        APIbase.__init__(self, cnx)
        self.partner_id = self._get([("ref", "=", ref),
            ("active", "=", True)], "res.partner")
        self.get_invoice_address()


class get_partner(APIbase):

    def __init__(self, id, cnx=None):
        APIbase.__init__(self, cnx)
        self.p = self._return_object('res.partner', id)

    def __getattr__(self, name):
        self.p["name"]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
