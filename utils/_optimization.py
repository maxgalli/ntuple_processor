import logging
logger = logging.getLogger(__name__)

class Node:
    def __init__(self,
            name, kind, afu_block, *children):
        self.name = name
        self.kind = kind
        self.afu_block = afu_block
        self.children = [
            child for child in children]

    def __str__(self):
        node_intest =     '////// Node Object ///////'
        end = ' //'
        bar_end = '///'
        safe_number_intest = len(node_intest)
        objects_intests = [
            '// Name:                  ',
            '// Kind:                  ',
            '// AnalysisFlowUnitBlock: ',
            '// Children:              '
            ]
        objects = [
            str(self.name),
            str(self.kind),
            str(self.afu_block),
            str(self.children)
            ]
        objects_tuples = [(oi, o) for oi,o in zip(objects_intests, objects)]
        safe_object = max(objects, key=len)
        safe_number = len(safe_object)

        def create_object_layout(intest, string):
            return intest + string \
                + (safe_number - len(string)) * ' ' \
                + end

        objects_layout = [create_object_layout(*tup) \
            for tup in objects_tuples]
        up_bar = node_intest \
                + safe_number * '/' \
                + bar_end
        down_bar = (safe_number_intest + safe_number) * '/' \
                    + bar_end
        layout = '\n'.join([
            up_bar, *objects_layout, down_bar
            ])

        return layout

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        logger.debug('__eq__ compares: names ({} with {}), kinds ({} and {}) and AFU blocks ({} and {})'.format(
                self.name, other.name,
                self.kind, other.kind,
                self.afu_block, other.afu_block))
        return self.name == other.name and \
            self.kind == other.kind and \
            self.afu_block == other.afu_block

    def __hash__(self):
        return hash((
            self.name, self.kind, self.afu_block))

