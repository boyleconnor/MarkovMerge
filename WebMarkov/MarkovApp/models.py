from io import TextIOWrapper
from django.db.models import Model, FileField, PositiveSmallIntegerField, ForeignKey, CASCADE
from picklefield.fields import PickledObjectField
from MarkovMerge.models.text_markov import TextMarkov
from MarkovMerge.models.text_merger import TextMerger

DEFAULT_NGRAM_SIZE = 5


class SingleMarkov(Model):
    ngram_size = PositiveSmallIntegerField(default=DEFAULT_NGRAM_SIZE)
    source_file = FileField(upload_to='sources/')
    markov_model = PickledObjectField()

    def save(self, *args, **kwargs):
        '''Enforces the following: .markov_model is a TextMarkov based off the
        contents of .source_file.
        '''
        if self.markov_model is None:
            self.markov_model = TextMarkov(self.ngram_size)
            wrapper = TextIOWrapper(self.source_file)  # FIXME: This seems hacky
            for line in wrapper:
                self.markov_model.read_text(line)
        return super().save(*args, **kwargs)


class MergedMarkov(Model):
    ngram_size = PositiveSmallIntegerField(default=DEFAULT_NGRAM_SIZE)
    source_one = ForeignKey(SingleMarkov, on_delete=CASCADE, related_name='merged_one')
    source_two = ForeignKey(SingleMarkov, on_delete=CASCADE, related_name='merged_two')
    merged_model = PickledObjectField()

    def save(self, *args, **kwargs):
        '''Enforces the following: .merged_model is a TextMerger based off
        .source_one and .source_two.
        '''
        if self.merged_model is None:
            self.merged_model = TextMerger(self.ngram_size,
                    TextIOWrapper(self.source_one.source_file),
                    TextIOWrapper(self.source_two.source_file))  # FIXME: The TextIOWrapper's seem hacky
        return super().save(*args, **kwargs)