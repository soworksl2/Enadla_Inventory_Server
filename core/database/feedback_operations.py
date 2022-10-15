from sys import argv

from core.helpers import own_json
from core.own_firebase_admin import db
from core.models import product_feedback

#region Collection Names as CN
is_debug = 'DEBUG' in argv

CN_PRODUCT_FEEDBACK = 'product_feedback' if not is_debug else 'test_product_feedback'
#endregion

def __get_product_feedback_equivalency_index(
    individual_product_feedback: product_feedback.IndividualProductFeedback,
    all_products_feedback_to_find: list[product_feedback.ProductFeedback]
    ):

    name_to_find = individual_product_feedback.name

    for index, specific_product_feedback in enumerate(all_products_feedback_to_find):
        if specific_product_feedback.product_name == name_to_find:
            return index

    return None

def __merge_individual_products_feedback_into_products_feedback(all_individual_products_feedback: list[product_feedback.IndividualProductFeedback], uid: str):
    all_products_feedback: list[product_feedback.ProductFeedback] = []

    for individual_products_feedback in all_individual_products_feedback:
        equivalency_index = __get_product_feedback_equivalency_index(individual_products_feedback, all_products_feedback)

        if equivalency_index is None:
            all_products_feedback.append(
                product_feedback.ProductFeedback.from_individual_product_feedback(individual_products_feedback, uid)
            )
        else:
            all_products_feedback[equivalency_index].update(individual_products_feedback, uid)

    return all_products_feedback

def __get_all_products_feedback_reference_affected_by(products_feedback_affecters: list[product_feedback.ProductFeedback]):
    output = []

    for product_feedback_affecter in products_feedback_affecters:
        output.append(db.collection(CN_PRODUCT_FEEDBACK).document(product_feedback_affecter.product_name))

    return output

#TODO: this function right now mutate the parameters. change it to keep the parameters inmutable 
#(the parameters that is mutate is changes).Jimy Aguasviva - 24 september 2022
def __applies_change_to_products_feedbacks_reference(products_feedback_references: list, changes: list[product_feedback.ProductFeedback]):
    if len(products_feedback_references) != len(changes):
        raise ValueError('the products_feedback_references and the changes cannot be of the diferent sizes')

    batch_update_operation = db.batch()

    for product_feedback_reference, change in zip(products_feedback_references, changes):
        product_feedback_snapshot = product_feedback_reference.get()
        
        if product_feedback_snapshot.exists:
            current_saved_product_feedback = product_feedback.ProductFeedback.from_dict(**product_feedback_snapshot.to_dict())
            change.update(current_saved_product_feedback)

        #TODO: to convert a ProductFeedback to a dict compatible with python it is firstly
        #converting to a serialized string to then deserialized. we have to change it with
        #more efficient way.
        change_dict = own_json.loads(own_json.dumps(change))

        batch_update_operation.set(product_feedback_reference, change_dict)

    batch_update_operation.commit()

def add_individual_products_feedback(uid, all_individual_products_feedback: list[product_feedback.IndividualProductFeedback]):

    changes_of_all_products_feedback = __merge_individual_products_feedback_into_products_feedback(all_individual_products_feedback, uid)

    saved_products_feedback_reference_to_operate = __get_all_products_feedback_reference_affected_by(changes_of_all_products_feedback)

    __applies_change_to_products_feedbacks_reference(
        saved_products_feedback_reference_to_operate,
        changes_of_all_products_feedback
    )

def get_all_products_feedback() -> list[product_feedback.ProductFeedback]:
    return [product_feedback.ProductFeedback.from_dict(**product_feedback_reference.get().to_dict())
    for product_feedback_reference in db.collection(CN_PRODUCT_FEEDBACK).list_documents()]

def delete_all_products_feedback():
    batch_delete_operation = db.batch()

    all_documents_to_delete = db.collection(CN_PRODUCT_FEEDBACK).list_documents()

    for document_to_delete in all_documents_to_delete:
        batch_delete_operation.delete(document_to_delete)

    batch_delete_operation.commit()