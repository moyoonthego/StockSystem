import json

# Implement the class below, keeping the constructor's signature unchanged; it should take no arguments.

class MarkingPositionMonitor:
    def __init__(self):
        self._marking_positions = dict()
        self._ids_to_orders = dict()
        self._order_status = dict()
        self._buyorder_amount = dict()
        self._sellorder_amount = dict()
        self._cancel_queue = []

    def on_event(self, message):
        '''
        (MarkingPositionMonitor, string) -> int
        This function takes a given message and creates an event to operate
        on the marking positions and orders with. It then returns the marking
        position of the desired order/stock
        REQ: message is formatted as a JSON string
        '''
        # Load json data into a dictionary variable
        total_data = json.loads(message)
        # get the operation type first
        operation_type = total_data("type")
        # Send operation to specified helper function, to operate on it
        if (operation_type == "NEW"):
            # helper functions also tell what company's mp the operation changed
            stock_name = self.new_operation(total_data);
        elif (operation_type == "ORDER_ACK"):
            stock_name = self.order_ack_operation(total_data);
        elif (operation_type == "ORDER_REJECT"):
            stock_name = self.order_reject_operation(total_data);
        elif (operation_type == "CANCEL"):
            stock_name = self.cancel_operation(total_data);
        elif (operation_type == "CANCEL_ACK"):
            stock_name = self.cancel_ack_operation(total_data);
        elif (operation_type == "CANCEL_REJECT"):
            stock_name = self.cancel_reject_operation(total_data);
        elif (operation_type == "FILL"):
            stock_name = self.fill_operation(total_data);
        # Otherwise, incorrect input in JSON file, raise error
        else:
            # Using nameerror, because cannot make new class for this exercise
            raise NameError("Incorrect operation detected")
        # After helper function has operated on command, want to return mp
        return self._marking_positions[stock_name]

    def new_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and places
        a new order
        REQ: quanitity is a positive value
        '''
        sell_or_buy = order_data["side"]
        company = order_data["symbol"]
        if company not in self._marking_positions:
            self._marking_positions[company] = 0
        self._ids_to_orders[order_data["order_id"]] = company
        if sell_or_buy == "SELL":
            # We are looking to buy stock
            # Update mp and save the order total
            self._marking_positions[company] -= order_data["quantity"]
            self._sellorder_amount[order_data["order_id"]] =\
                order_data["quantity"]
            # Assign order status false (not yet acknowledged)
            self._order_status[order_data["order_id"]] = False;
        else:
            self._buyorder_amount[order_data["order_id"]] =\
                order_data["quantity"]
            # Assign order status false (not yet acknowledged)
            self._order_status[order_data["order_id"]] = False;
        return company

    def order_ack_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and
        acknowledges an order
        '''
        # First, change the order to read as accepted in order status
        self._order_status[order_data["order_id"]] = True;
        # get compnay name
        company = self._ids_to_orders[order_data["order_id"]]
        # If it was a buy order, update the amount of mp
        if order_data["order_id"] in self._buyorder_amount:
            self._marking_positions[company] +=\
                self._buyorder_amount[order_data["order_id"]]
        # finally return company name
        return company

    def order_reject_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and
        rejects an order
        '''
        # get compnay name
        company = self._ids_to_orders[order_data["order_id"]]
        # If it was a sell order, update the amount of mp
        if order_data["order_id"] in self._sellorder_amount:
            self._marking_positions[company] +=\
                self._sellorder_amount[order_data["order_id"]]
        # finally return company name
        return company

    def cancel_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and requests
        to cancel previous order
        '''
        # get compnay name
        company = self._ids_to_orders[order_data["order_id"]]
        self._cancel_queue.append(order_data["order_id"])
        # finally return company name
        return company

    def cancel_reject_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and requests
        to cancel previous order
        '''
        # get compnay name
        company = self._ids_to_orders[order_data["order_id"]]
        # Only fulfill if it was in our queue of cancellations
        if order_data["order_id"] in self._cancel_queue:
            # remove this cancellation request (it is handled)
            self._cancel_queue.pop(order_data["order_id"])
        # finally return company name
        return company

    def cancel_ack_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and requests
        to cancel previous order
        '''
        # get compnay name
        company = self._ids_to_orders[order_data["order_id"]]
        # Only fulfill if it was in our queue of cancellations
        if order_data["order_id"] in self._cancel_queue:
            # If it was a buy order, update the amount of mp
            if (order_data["order_id"] in self._buyorder_amount):
                self._marking_positions[company] -=\
                    self._buyorder_amount[order_data["order_id"]]
            # do the same with selling orders
            if (order_data["order_id"] in self._sellorder_amount):
                self._marking_positions[company] +=\
                    self._sellorder_amount[order_data["order_id"]]
            # remove this cancellation request (it is handled)
            self._cancel_queue.pop(order_data["order_id"])
        # finally return company name
        return company

    def fill_operation(self, order_data):
        '''
        (MarkingPositionMonitor, dict) -> string
        This function takes a given dict of relevant information and lets user
        know if the operation was fulfilled
        '''
        # get compnay name
        company = self._ids_to_orders[order_data["order_id"]]
        # If it was a buying or selling fulfillment...
        if (order_data["order_id"] in self._buyorder_amount) or\
           (order_data["order_id"] in self._sellorder_amount):
            # add filled amount, remove unfilled amount
            self._marking_positions += (order_data["filled_quantity"] -\
                order_data["remaining_quantity"])
        # finally, return company name
        return company
