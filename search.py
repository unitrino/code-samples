import numpy

from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES


class WorkWithSignatures():
    n_grid = 9
    crop_percentile = (5, 95)
    P = None
    diagonal_neighbors = True
    identical_tolerance = 2 / 255
    n_levels = 2
    search_rotated = False

    es = Elasticsearch(
        ['elasticsearch_img'],
        port=9200,
    )
    # es = Elasticsearch()

    ses = SignatureES(es, n_grid=n_grid, crop_percentile=crop_percentile, diagonal_neighbors=diagonal_neighbors,
                      identical_tolerance=identical_tolerance, n_levels=n_levels, distance_cutoff=0.9999)

    def clear_db(self):
        self.es.indices.delete(index='images', ignore=[400, 404])

    def reload_params(self, params):
        self.n_grid = params['n_grid']
        self.crop_percentile = params['crop_percentile']
        self.P = params['P']
        self.diagonal_neighbors = params['diagonal_neighbors']
        self.identical_tolerance = params['identical_tolerance']
        self.n_levels = params['n_levels']
        params.pop("search_rotated", None)
        self.ses = SignatureES(self.es, **params)

    def get_all_params(self):
        return {'n_grid': self.n_grid,
                'crop_percentile': self.crop_percentile,
                'P': self.P,
                'diagonal_neighbors': self.diagonal_neighbors,
                'identical_tolerance': self.identical_tolerance,
                'n_levels': self.n_levels}

    def set_rotate_param(self, rotate):
        self.search_rotated = rotate

    def get_rotate_param(self):
        return self.search_rotated

    def load_file(self, path):
        self.ses.add_image(path)

    def search_file(self, file_bytes):
        return self.ses.search_image(file_bytes, bytestream=True, all_orientations=self.search_rotated)

    def search_file_with_threshold(self, file_bytes, threshold):
        if threshold == 0.0:
           return self.ses.search_image(file_bytes, bytestream=True, all_orientations=self.search_rotated)
        else:
            ses = SignatureES(self.es, distance_cutoff=threshold)
            return ses.search_image(file_bytes, bytestream=True, all_orientations=self.search_rotated)

    def search_file_with_threshold_and_rotated(self, file_bytes, threshold, search_rotated):
        if threshold == 0.0:
           return self.ses.search_image(file_bytes, bytestream=True, all_orientations=search_rotated)
        else:
            ses = SignatureES(self.es, distance_cutoff=threshold)
            return ses.search_image(file_bytes, bytestream=True, all_orientations=search_rotated)

    def get_summary_count(self):
        return self.es.search(index="images*", size=0)['hits']['total']

    def delete_file_from_es(self, path):
        matching_paths = [item['_id'] for item in
                          self.es.search(body={'query':
                                               {'match':
                                                {'path': path}
                                               }
                                              },
                                         index='images')['hits']['hits']
                          if item['_source']['path'] == path]
        if len(matching_paths) > 0:
            for id_tag in matching_paths:
                self.es.delete(index='images', doc_type='image', id=id_tag)
        else:
            raise Exception("File does not exists")

    def delete_duplicate_signature(self):
        all_data = self.es.search(index="images", body={"query": {"match_all": {}}})
        ids_and_sings = [(d['_id'], d['_source']['signature']) for d in all_data['hits']['hits']]
        to_delete =[elem[0] for index, elem in enumerate(ids_and_sings) for j in ids_and_sings[index+1:] if numpy.array_equal(elem[1], j[1])]
        for id_tag in set(to_delete):
            self.es.delete(index='images', doc_type='image', id=id_tag)
        paths = [d['_source']['path'] for d in all_data['hits']['hits']]
        for path in paths:
            self.ses.delete_duplicates(path)

