from oobjlib.component import Object
from settings import make_cnx


class APIbase(object):
    def __init__(self, cnx=None):
        """
        cnx is a connection object used to communicate with the openERP server
        common is the objectName-common name mapping to make
        errors easier to use/act on

        """

        if cnx is None:
            self.cnx = make_cnx()
        else:
            self.cnx = cnx

        self.common = {
            'res.partner': 'Partner',
            'res.partner.address': 'Address',
            'res.country':  'Country',
            'account.invoice': 'Invoice',
            'account.account': 'Account',
            'product.uom': 'Unit of Measure',
            'product.product': 'Product',
            'product.supplierinfo': 'SupplierInfo',
            'pricelist.partnerinfo': 'Pricelist',
            'sale.order': 'Sales Order',
            'sale.order.line': 'Sales Order Line',
            'product.template': 'Product Template',
            'product.variant.dimension.type': 'Product Variants',
            'account.voucher.line': 'Voucher Line Item',
            'account.voucher': 'Voucher',
            'account.journal': 'Journal',
            'account.move.line': 'Journal Item',
            'account.invoice.tax': 'tax',
            'stock.location': 'Stock Location',
            'stock.inventory': "Inventory",
            'stock.inventory.line': 'Inventory Line',
            'stock.production.lot': 'Production Lot',
            'product.category': 'Category',
            'stock.move': 'Stock Move',
            'ir.attachment': 'Attachment',
            'account.account.type': 'Account Type',
            'account.analytic.account': 'Analytic Account',
            'product.pricelist': 'Pricelist',
            'sale.shop': 'Shop',
            'stock.warehouse': 'Stock Warehouse',
            'product.uom.categ':  'Product UOM categories',
            'res.company': 'Company',
            'res.country.state': 'State',
            'res.users': 'Users',
            'purchase.order': 'Purchase Order',
            'purchase.order.line': 'Purchase Order Line',
            'account.payment.term': 'Payment Term',
            'account.invoice.line':  'Invoice Line',
            'account.fiscal.position': 'account.fiscal.position',
            'lost_and_found': 'Lost and Found Document',
            'account.location': 'Account Location',
            'account.asset.asset': 'Asset',
            'account.asset.category': 'Asset Category',
            'res.partner.category': 'Partner Category',
            'account.move': 'Journal Entry',
            'account.period': 'Account Period',
            'account.bank.statement': 'Account Bank Statement',
        }

    def _create(self, args, objectName):
        """
        To create a new object, pass in a dictionary of objects and use the
        objectName to create the object.
        """

        arguments = self.__parse_options(args)

        obj = Object(self.cnx, objectName)

        objectCreated = obj.create(arguments)

        if objectCreated:
            return objectCreated
        else:
            raise EnvironmentError("We attempted to create a " + \
               self.common[objectName] + " but failed.")

    def _exists(self, searchTuples, objectName):
        """
        Returns true if the search has a result.
        """

        obj = Object(self.cnx, objectName)
        try:
            if obj.search(searchTuples):
                return True
        except:
            return False

    def _get(self, searchTuples, objectName):
        """
        returns the object id as int iff the search returns a single result.
        """
        obj = Object(self.cnx, objectName)
        results = obj.search(searchTuples)

        if len(results) != 1:
            raise ValueError("We did not get a single " + \
                self.common[objectName] + " back. " + \
                str(results) + str(searchTuples))
        else:
            return results[0]

    def _get_attr(self, searchTuples, objectName, attribute):
        """
        returns value of the attribute
        """
        obj = Object(self.cnx, objectName)
        results = obj.search(searchTuples)

        if len(results) != 1:
            raise ValueError("We did not get a single " + \
                self.common[objectName] + " back. " + \
                str(results))
        else:
            return obj.read(results[0])[attribute]

    def _update(self, searchTuples, args, objectName):
        """
        A sub function that updates the object if it exists
        """

        obj = Object(self.cnx, objectName)
        commonName = self.common[objectName]
        results = obj.search(searchTuples)
        arguments = self.__parse_options(args)
        if results:
            if isinstance(results, list):
                results = results
            else:
                results = [results]
            if len(results) == 1:
                if obj.write(results, arguments):
                    return results[0]

                else:
                    raise EnvironmentError("We attempted to update a  " + \
                        + commonName + \
                        " , but failed.")
            else:
                string = ":"
                for obj in results:
                    string += str(obj) + ", "

                string += " Search: "
                for obj in searchTuples:
                    string += str(obj) + ", "

                raise ValueError("We preformed a search for a " + commonName + \
                    "and came back with a number greater than one." \
                    + string)

    def _update_no_search(self, id, args, objectName):
        """
        To update an object when we already know the id
        """

        obj = Object(self.cnx, objectName)
        commonName = self.common[objectName]
        results = id
        arguments = self.__parse_options(args)
        if results:
            if isinstance(results, list):
                results = results
            else:
                results = [results]
            if len(results) == 1:
                if obj.write(results, arguments):
                    return results[0]

                else:
                    raise EnvironmentError("We attempted to update a  " + \
                        + commonName + \
                       " , but failed.")
            else:
                string = ""
                for obj in results:
                    string += obj

                raise ValueError("We preformed a search for a " + commonName + \
                                "and came back with a number greater than one." \
                                + string)

    def _replace_or_create(self, search, objectName, args):
        """
        A Wrapper on previous functions.  Checks if obj exists, if so updates,
        else it creates.
        """

        if self._exists(search, objectName):
            return self._update(search, args, objectName)
        else:
            return self._create(args, objectName)

    def __parse_options(self, args):
        """
        reads out 'options' and puts them into a dictionary
        Also: removes the object from the dictionary if the value = None
        """
        tempDict = {}

        for key, value in args.iteritems():
            if value is None:
                continue
            elif key == 'options':
                if value:
                    for k, v in value.iteritems():
                        tempDict[k] = v
            else:
                tempDict[key] = value

        return tempDict

    def _copy_with_args(self, searchTuples, searchExists, args, objectName):
        """
        Does a copy and then adds some extra information.
        """
        obj = Object(self.cnx, objectName)
        results = obj.search(searchTuples)
        new_id = obj.copy(results[0])

        if self._exists(searchExists, objectName):
            return True
        else:
            return self._update_no_search(new_id, args, objectName)

    def _return_object(self, objectName, id):
        obj = Object(self.cnx, objectName)
        r = obj.search([("id", "=", id)])
        return obj.read(r)[0]

    def _get_period(self, date):
        d = str(date.date())
        obj = Object(self.cnx, 'account.period')

        ids = obj.search([("date_start", "<=", d), ("date_stop", ">=", d),
            ("state", "=", "draft"), ("special", "=", False)])

        if len(ids) == 1:
            return ids[0]
        else:
            raise ValueError(
                "Did not find a single open period with that date, %s" % d)
