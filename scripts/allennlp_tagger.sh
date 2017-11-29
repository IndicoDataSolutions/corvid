# train a simple allennlp sequence tagger.
python -m allennlp.run train -s ./temp_serialization_dir ./allennlp_tagger/results_tagger.config
# evaluate the tagger.
python -m allennlp.run evaluate --archive_file ./temp_serialization_dir/model.tar.gz --evaluation_data_file ./data/papers-2017-10-30.induced_labels.dev
