from unittest import TestCase
from mock import MagicMock, patch

from cthulhu.manager.crush_node_request_factory import CrushNodeRequestFactory
from cthulhu.manager.user_request import RadosRequest


class TestCrushNodeFactory(TestCase):

    fake_salt = MagicMock(run_job=MagicMock())
    fake_salt.return_value = fake_salt
    fake_salt.run_job.return_value = {'jid': 12345}

    def setUp(self):
        crush_node_by_id = {-1:
                            {'name': 'root',
                             'type_name': 'root',
                             'items': [{'id': -3,
                                        'weight': 3,
                                        'pos': 1},
                                       {'id': -2,
                                        'weight': 2,
                                        'pos': 0}]
                             },
                            -2: {'name': 'rack1', 'items': []},
                            -4: {'name': 'rack3', 'items': []},
                            -3: {'name': 'rack2', 'items': []}}

        osd_map_attrs = {'get_tree_node': lambda x: crush_node_by_id[x],
                         'osd_tree_node_by_id': {2: {'name': 'osd.2'},
                                                 3: {'name': 'osd.3'}},
                         'parent_bucket_by_node_id': {-2: {'name': 'root', 'type': 'root'}},
                         'osds_by_id': {0: {'up': True}, 1: {'up': False}}}
        fake_osd_map = MagicMock()
        fake_osd_map.configure_mock(**osd_map_attrs)

        fake_cluster_monitor = MagicMock()
        attributes = {'name': 'I am a fake',
                      'fsid': 12345,
                      'get_sync_object.return_value': fake_osd_map}
        fake_cluster_monitor.configure_mock(**attributes)

        self.factory = CrushNodeRequestFactory(fake_cluster_monitor)

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_create_new_root(self):
        attribs = {'name': 'fake',
                   'bucket-type': 'root',
                   "items": [{"id": -2,
                              "weight": 6553,
                              "pos": 0
                              },
                             {"id": -3,
                              "weight": 0,
                              "pos": 1
                              }
                             ]
                   }
        create_node = self.factory.create(attribs)
        self.assertIsInstance(create_node, RadosRequest, 'creating crush node')

        create_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0][2][2] == \
            [('osd crush add-bucket', {'name': 'fake', 'type': 'root'}),
             ('osd crush move', {'args': ['root=fake'], 'name': 'rack1'}),
             ('osd crush move', {'args': ['root=fake'], 'name': 'rack2'}),
             ]

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_create_new_host(self):
        attribs = {'name': 'fake',
                   'bucket-type': 'host',
                   "items": [{"id": 2,
                              "weight": 22,
                              "pos": 0
                              },
                             {"id": 3,
                              "weight": 33,
                              "pos": 1
                              }
                             ]
                   }
        create_node = self.factory.create(attribs)
        self.assertIsInstance(create_node, RadosRequest, 'creating crush node')
        create_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0] == \
            (54321,
             'ceph.rados_commands',
             [12345,
              'I am a fake',
              [('osd crush add-bucket', {'name': 'fake', 'type': 'host'}),
               ('osd crush reweight', {'name': 'osd.2', 'weight': 0.0}),
               ('osd crush remove', {'name': 'osd.2'}),
               ('osd crush add', {'args': ['host=fake'], 'id': 2, 'weight': 0.0}),
               ('osd crush reweight', {'name': 'osd.2', 'weight': 22}),
               ('osd crush reweight', {'name': 'osd.3', 'weight': 0.0}),
               ('osd crush remove', {'name': 'osd.3'}),
               ('osd crush add', {'args': ['host=fake'], 'id': 3, 'weight': 0.0}),
               ('osd crush reweight', {'name': 'osd.3', 'weight': 33})]])

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_update_rename(self):
        attribs = {'name': 'renamed',
                   'bucket-type': 'root',
                   "items": [{"id": -2,
                              "weight": 2,
                              "pos": 0
                              },
                             {"id": -3,
                              "weight": 3,
                              "pos": 1
                              }
                             ]
                   }
        update_node = self.factory.update(-1, attribs)
        self.assertIsInstance(update_node, RadosRequest, 'renaming crush node')

        update_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0][2][2] == \
            [('osd crush add-bucket', {'name': 'renamed', 'type': 'root'}),
             ('osd crush move', {'args': ['root=renamed'], 'name': 'rack1'}),
             ('osd crush move', {'args': ['root=renamed'], 'name': 'rack2'}),
             ('osd crush remove', {'name': 'root'}),
             ]

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_update_add_items(self):
        attribs = {'name': 'root',
                   'bucket-type': 'root',
                   "items": [{"id": -2,
                              "weight": 2,
                              "pos": 0
                              },
                             {"id": -3,
                              "weight": 3,
                              "pos": 1
                              },
                             {"id": -4,
                              "weight": 4,
                              "pos": 2
                              }
                             ]
                   }
        update_node = self.factory.update(-1, attribs)
        self.assertIsInstance(update_node, RadosRequest, 'adding items to crush node')

        update_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0][2][2] == \
            [('osd crush move', {'args': ['root=root'], 'name': 'rack1'}),
             ('osd crush move', {'args': ['root=root'], 'name': 'rack2'}),
             ('osd crush move', {'args': ['root=root'], 'name': 'rack3'}),
             ]

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_update_remove_items(self):
        attribs = {'name': 'root',
                   'bucket-type': 'root',
                   "items": [{"id": -2,
                              "weight": 2,
                              "pos": 0
                              },
                             ]
                   }
        update_node = self.factory.update(-1, attribs)
        self.assertIsInstance(update_node, RadosRequest, 'removing items from crush node')

        update_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0][2][2] == \
            [('osd crush remove', {'name': 'rack2'}),
             ('osd crush move', {'args': ['root=root'], 'name': 'rack1'}),
             ]

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_update_remove_osds(self):
        attribs = {'name': 'root',
                   'bucket-type': 'root',
                   "items": [{"id": -2,
                              "weight": 2,
                              "pos": 0
                              },
                             ]
                   }
        update_node = self.factory.update(-1, attribs)
        self.assertIsInstance(update_node, RadosRequest, 'removing items from crush node')

        update_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0][2][2] == \
            [('osd crush remove', {'name': 'rack2'}),
             ('osd crush move', {'args': ['root=root'], 'name': 'rack1'}),
             ]

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_delete_bucket(self):
        delete_node = self.factory.delete(-2)
        self.assertIsInstance(delete_node, RadosRequest, 'renaming crush node')

        delete_node.submit(54321)
        assert self.fake_salt.run_job.call_args[0][2][2] == [('osd crush remove', {'name': 'rack1'})]

    @patch('cthulhu.manager.user_request.LocalClient', fake_salt)
    def test_update_rename_relink_to_parent(self):
        attribs = {'name': 'renamed',
                   'bucket-type': 'rack',
                   "items": [{"id": 2,
                              "weight": 22,
                              "pos": 0
                              },
                             {"id": 3,
                              "weight": 33,
                              "pos": 1
                              }
                             ]
                   }
        update_node = self.factory.update(-2, attribs)
        self.assertIsInstance(update_node, RadosRequest, 'renaming crush node')

        update_node.submit(54321)
        self.assertEqual(self.fake_salt.run_job.call_args[0][2][2], [
            ('osd crush add-bucket', {'name': 'renamed', 'type': 'rack'}),
            ('osd crush move', {'args': ['root=root'], 'name': 'renamed'}),
            ('osd crush reweight', {'name': 'osd.2', 'weight': 0.0}),
            ('osd crush remove', {'name': 'osd.2'}),
            ('osd crush add', {'args': ['rack=renamed'], 'id': 2, 'weight': 0.0}),
            ('osd crush reweight', {'name': 'osd.2', 'weight': 22}),
            ('osd crush reweight', {'name': 'osd.3', 'weight': 0.0}),
            ('osd crush remove', {'name': 'osd.3'}),
            ('osd crush add', {'args': ['rack=renamed'], 'id': 3, 'weight': 0.0}),
            ('osd crush reweight', {'name': 'osd.3', 'weight': 33}),
            ('osd crush remove', {'name': 'rack1'}),
        ]
        )
