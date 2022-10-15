from dataclasses import dataclass

from core.helpers import model_helper

@dataclass
class SingleComputedProduct:
    internal_id: int
    bar_code: str
    name: str
    aliases: list[str]
    bad_spellings: list[str]
    computed_cost: float

    @classmethod
    def from_dict(cls, **kwargs):
        output = model_helper.create_obj(cls, False, **kwargs)

        return output
        

@dataclass
class ComputedProducts:
    ignored_users: list[str] = None
    ignored_products: list[str] = None
    products: list[SingleComputedProduct] = None

    @classmethod
    def from_dict(cls, **kwargs):
        output = model_helper.create_obj(cls, False, **kwargs)

        if output.products is not None and not isinstance(output.products, list):
            raise ValueError('products should be a list of SingleComputedProducts')

        if output.products is not None:
            for index in range(0, len(output.products)):
                current_single_product = output.products[index]
                if isinstance(current_single_product, cls):
                    continue

                if not isinstance(current_single_product, dict):
                    raise TypeError('if products contains not SingleComputedProduct type then should be a dict to try to parse')

                output.products[index] = SingleComputedProduct.from_dict(**current_single_product)

        return output

                