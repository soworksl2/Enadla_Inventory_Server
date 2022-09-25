#TODO: this module need to be refactored with urgency and
#create unit testing for all this module. Jimy Aguasviva - 23 september 2022

#TODO: in the all structure to save into firestore we have to save the
#range of dates that indicate when the product cost feedbacked was that. Jimy Aguasviva - 24 september 2022

from dataclasses import dataclass

from helpers import model_helper

@dataclass
class ProductFeedbacker:

    uid: str
    concurrency: int

    @classmethod
    def from_dict(cls, **kwargs):
        return model_helper.create_obj(cls, False, **kwargs)

@dataclass
class CostProductFeedback:

    cost: float
    concurrency: int
    feedbackers: list[ProductFeedbacker]

    @classmethod
    def from_dict(cls, **kwargs):
        output = model_helper.create_obj(cls, False, **kwargs)

        if output.feedbackers is not None and not isinstance(output.feedbackers, list):
            raise TypeError('feedbackers should be none or a list')

        if output.feedbackers is not None:
            new_feedbackers = []
            for feedbackers in output.feedbackers:
                if isinstance(feedbackers, ProductFeedbacker):
                    new_feedbackers.append(feedbackers)
                elif isinstance(feedbackers, dict):
                    new_feedbackers.append(ProductFeedbacker.from_dict(**feedbackers))
                else:
                    raise TypeError('feedbackers should be a list of ProductFeedbackers or at least a dict to convert it')

            output.feedbackers = new_feedbackers

        return output

    def add_feedbackers(self, feedbacker_to_add: ProductFeedbacker):
        for product_feedbacker in self.feedbackers:
            if product_feedbacker.uid == feedbacker_to_add.uid:
                product_feedbacker.concurrency += feedbacker_to_add.concurrency
                return

        self.feedbackers.append(feedbacker_to_add)

    def update(self, cost_product_feedback_to_add):
        if not isinstance(cost_product_feedback_to_add, CostProductFeedback):
            raise TypeError('cost_product_feedback_to_add should be CostProductFeedback')

        if cost_product_feedback_to_add.cost != self.cost:
            raise ValueError('the cost_product_feedback to add is not compatible with the current cost_product_feedback')
        
        self.concurrency += cost_product_feedback_to_add.concurrency

        for product_feedbacker in cost_product_feedback_to_add.feedbackers:
            self.add_feedbackers(product_feedbacker)

@dataclass
class IndividualProductFeedback:
    name: str
    cost: float
    repetition: int

    @classmethod
    def from_dict(cls, **kwargs):
        return model_helper.create_obj(cls, False, **kwargs)

@dataclass
class ProductFeedback:

    product_name: str
    all_costs: list[CostProductFeedback]

    @classmethod
    def from_dict(cls, **kwargs):
        output = model_helper.create_obj(cls, False, **kwargs)

        if output.all_costs is not None and not isinstance(output.all_costs, list):
            raise TypeError('all_costs should be none or a list')

        if output.all_costs is not None:
            new_all_costs = []
            for cost_product_feedback in output.all_costs:
                if isinstance(cost_product_feedback, CostProductFeedback):
                    new_all_costs.append(cost_product_feedback)
                elif isinstance(cost_product_feedback, dict):
                    new_all_costs.append(CostProductFeedback.from_dict(**cost_product_feedback))
                else:
                    raise TypeError('all_cost should be a list of CostProductFeedback or at least a dict to convert it')

            output.all_costs = new_all_costs

        return output

    @classmethod
    def from_individual_product_feedback(cls, current_individual_product_feedback: IndividualProductFeedback, uid: str):
        """transform an IndividualProductFeedback to a ProductFeedback

        Args:
            current_individual_product_feedback (IndividualProductFeedback): The IndividualProductFeedback from where transform
            uid (str): The user identifier that send this IndividualProductFeedback

        Returns:
            ProductFeedback: The transformed ProductFeedback
        """

        return ProductFeedback(
            current_individual_product_feedback.name,
            [
                CostProductFeedback(
                    current_individual_product_feedback.cost,
                    current_individual_product_feedback.repetition,
                    [
                        ProductFeedbacker(
                            uid,
                            current_individual_product_feedback.repetition
                        )
                    ]
                )
            ]
        )

    def add_cost_product_feedback(self, cost_to_add: CostProductFeedback):
        
        for cost in self.all_costs:
            if cost.cost != cost_to_add.cost:
                continue

            cost.concurrency += cost_to_add.concurrency
            for product_feedbacker in cost_to_add.feedbackers:
                cost.add_feedbackers(product_feedbacker)
            return

        self.all_costs.append(cost_to_add)

    def __get_equivalency_index_in_all_cost(self, cost_to_find: CostProductFeedback):
        for index, cost in enumerate(self.all_costs):
            if cost.cost == cost_to_find.cost:
                return index
        
        return None

    def __update_with_ProductFeedback(self, changes):
        if not isinstance(changes, ProductFeedback):
            raise TypeError('changes should be ProductFeedback')

        if self.product_name != changes.product_name:
            raise ValueError('the change is not compatible with the current ProductFeedback')

        for cost_product_feedback in changes.all_costs:
            equivalency_index_cost = self.__get_equivalency_index_in_all_cost(cost_product_feedback)

            if equivalency_index_cost is None:
                self.all_costs.append(cost_product_feedback)
            else:
                self.all_costs[equivalency_index_cost].update(cost_product_feedback)

    def __update_with_IndividualFeedback(self, changes, uid):
        
        if not uid:
            raise ValueError('uid cannot be None or empty')

        if not isinstance(changes, IndividualProductFeedback):
            raise TypeError('changes should be an IndividualProductFeedback')

        if changes.name != self.product_name:
            raise ValueError(f'the IndividualProductFeedback "{changes.name}" is diferent than "{self.product_name}"')

        cost_product_feedback_to_add = CostProductFeedback(
            changes.cost,
            changes.repetition,
            [
                ProductFeedbacker(
                    uid,
                    changes.repetition
                )
            ]
        )

        self.add_cost_product_feedback(cost_product_feedback_to_add)

    def update(self, changes, uid: str = None):
        if isinstance(changes, ProductFeedback):
            self.__update_with_ProductFeedback(changes)
        elif isinstance(changes, IndividualProductFeedback):
            self.__update_with_IndividualFeedback(changes, uid)
        else:
            raise TypeError('changes should be ProductFeedback or IndividualProductFeedback')

#TODO: make validation function to validate the ProductFeedback and IndividualProductFeedback. Jimy Aguasviva - 20 september 2022