Examples for api/v2/cluster/<fsid>/sync_object/<sync_type>
==========================================================

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/config
----------------------------------------------------------------------

.. code-block:: json

   {
     "auth_mon_ticket_ttl": "43200", 
     "mds_tick_interval": "5", 
     "ms_inject_delay_max": "1", 
     "rgw_swift_auth_url": "", 
     "mds_log_expire": "1/5", 
     "osd_debug_pg_log_writeout": "false", 
     "filestore_wbthrottle_xfs_inodes_start_flusher": "500", 
     "rbd_default_stripe_count": "1", 
     "mon_osd_laggy_weight": "0.3", 
     "mon_max_pgmap_epochs": "500", 
     "osd": "0/5", 
     "mon_accept_timeout": "10", 
     "mon_daemon_bytes": "419430400", 
     "client_cache_size": "16384", 
     "rbd_concurrent_management_ops": "10", 
     "osd_use_stale_snap": "false", 
     "tp": "0/5", 
     "auth_client_required": "cephx", 
     "rgw_gc_processor_max_time": "3600", 
     "client_readahead_max_periods": "4", 
     "mon_probe_timeout": "2", 
     "osd_command_max_records": "256", 
     "mon_osd_laggy_halflife": "3600", 
     "rgw_keystone_admin_token": "", 
     "osd_recover_clone_overlap_limit": "10", 
     "client_oc_max_dirty_age": "5", 
     "rgw_swift_url_prefix": "swift", 
     "mon_debug_dump_location": "/var/log/ceph/myceph-mon.gravel1.tdump", 
     "cephx_service_require_signatures": "false", 
     "mon_subscribe_interval": "300", 
     "paxos_max_join_drift": "10", 
     "rgw_gc_obj_min_wait": "7200", 
     "mds_kill_journal_replay_at": "0", 
     "mds_locker": "1/5", 
     "auth_service_required": "cephx", 
     "filestore_debug_inject_read_err": "false", 
     "mon_clock_drift_warn_backoff": "5", 
     "filestore_queue_max_bytes": "104857600", 
     "rgw_log_object_name": "%Y-%m-%d-%H-%i-%n", 
     "osd_age": "0.8", 
     "osd_default_data_pool_replay_window": "45", 
     "osd_pool_default_min_size": "0", 
     "filestore_update_to": "1000", 
     "mds_bal_need_max": "1.2", 
     "osd_leveldb_compression": "true", 
     "mds_mem_max": "1048576", 
     "filestore_wbthrottle_btrfs_ios_hard_limit": "5000", 
     "osd_max_pgls": "1024", 
     "filestore_fsync_flushes_journal_data": "false", 
     "objectcacher": "0/5", 
     "osd_recovery_op_priority": "10", 
     "rgw_enable_ops_log": "false", 
     "mds_dump_cache_after_rejoin": "false", 
     "filestore_wbthrottle_btrfs_bytes_start_flusher": "41943040", 
     "mon_clock_drift_allowed": "0.05", 
     "rgw_init_timeout": "300", 
     "osd_verify_sparse_read_holes": "false", 
     "mds_replay_interval": "1", 
     "mon_leveldb_max_open_files": "0", 
     "osd_max_scrubs": "1", 
     "mds_kill_journal_at": "0", 
     "osd_leveldb_max_open_files": "0", 
     "log_to_syslog": "false", 
     "crush": "1/1", 
     "osd_debug_verify_snaps_on_info": "false", 
     "filestore_blackhole": "false", 
     "paxos_kill_at": "0", 
     "osd_max_push_objects": "10", 
     "rgw_intent_log_object_name": "%Y-%m-%d-%i-%n", 
     "osd_heartbeat_addr": ":/0", 
     "mon_osd_down_out_interval": "300", 
     "rgw_bucket_quota_ttl": "600", 
     "fatal_signal_handlers": "true", 
     "mds_bal_merge_wr": "1000", 
     "osd_pg_bits": "6", 
     "paxos_service_trim_max": "500", 
     "rbd": "0/5", 
     "mon_pg_create_interval": "30", 
     "filestore_debug_omap_check": "false", 
     "rgw_ops_log_rados": "true", 
     "osd_op_history_size": "20", 
     "mds_kill_journal_expire_at": "0", 
     "daemonize": "false", 
     "rbd_default_format": "1", 
     "osd_age_time": "0", 
     "rgw_keystone_token_cache_size": "10000", 
     "mds_bal_minchunk": "0.001", 
     "filestore_wbthrottle_xfs_inodes_hard_limit": "5000", 
     "filestore_split_multiple": "2", 
     "rgw_mime_types_file": "/etc/mime.types", 
     "osd_disk_threads": "1", 
     "mon_osd_nearfull_ratio": "0.85", 
     "objecter_inflight_ops": "1024", 
     "osd_mon_shutdown_timeout": "5", 
     "rgw_ops_log_data_backlog": "5242880", 
     "perf": "true", 
     "filestore_max_inline_xattr_size_btrfs": "2048", 
     "osd_check_for_log_corruption": "false", 
     "osd_auto_weight": "false", 
     "rgw_keystone_accepted_roles": "Member, admin", 
     "journal_queue_max_ops": "300", 
     "pid_file": "", 
     "osd_push_per_object_cost": "1000", 
     "max_mds": "1", 
     "cephx_cluster_require_signatures": "false", 
     "rgw_s3_auth_use_rados": "true", 
     "mon_max_pool_pg_num": "65536", 
     "mon_cluster_log_file_level": "info", 
     "mds_kill_export_at": "0", 
     "rbd_cache_max_dirty_age": "1", 
     "mds_inject_traceless_reply_probability": "0", 
     "none": "0/5", 
     "chdir": "/", 
     "mds_kill_mdstable_at": "0", 
     "mon_leveldb_bloom_size": "0", 
     "rgw_dns_name": "", 
     "osd_pool_default_pg_num": "8", 
     "rados": "0/5", 
     "ms": "0/5", 
     "osd_backfill_full_ratio": "0.85", 
     "mon_data": "/var/lib/ceph/mon/myceph-gravel1", 
     "filestore_journal_parallel": "false", 
     "journaler_prefetch_periods": "10", 
     "clock_offset": "0", 
     "mon_data_avail_warn": "30", 
     "fuse_big_writes": "true", 
     "inject_early_sigterm": "false", 
     "osd_backfill_scan_max": "512", 
     "rgw_log_object_name_utc": "false", 
     "journal_max_corrupt_search": "10485760", 
     "filestore_wbthrottle_btrfs_inodes_hard_limit": "5000", 
     "filestore_wbthrottle_xfs_ios_hard_limit": "5000", 
     "heartbeat_inject_failure": "0", 
     "mon_pool_quota_warn_threshold": "0", 
     "mds_bal_max_until": "-1", 
     "mon_lease_ack_timeout": "10", 
     "ms_rwthread_stack_bytes": "1048576", 
     "osd_op_pq_min_cost": "65536", 
     "mds_early_reply": "true", 
     "rgw_usage_log_flush_threshold": "1024", 
     "rgw_data": "/var/lib/ceph/radosgw/myceph-gravel1", 
     "mon_sync_debug_provider_fallback": "-1", 
     "paxos_min": "500", 
     "mon_leveldb_cache_size": "536870912", 
     "filestore": "false", 
     "osd_max_push_cost": "8388608", 
     "osd_scan_list_ping_tp_interval": "100", 
     "osd_max_object_size": "107374182400", 
     "osd_journal": "/var/lib/ceph/osd/myceph-gravel1/journal", 
     "journal_zero_on_create": "false", 
     "osd_op_pq_max_tokens_per_priority": "4194304", 
     "mds_dirstat_min_interval": "1", 
     "filestore_fiemap_threshold": "4096", 
     "osd_debug_drop_ping_probability": "0", 
     "keyfile": "", 
     "osd_debug_drop_pg_create_probability": "0", 
     "log_stop_at_utilization": "0.97", 
     "journaler_allow_split_entries": "true", 
     "osd_scrub_max_interval": "604800", 
     "auth_cluster_required": "cephx", 
     "osd_leveldb_bloom_size": "0", 
     "fuse_atomic_o_trunc": "true", 
     "mon_pool_quota_crit_threshold": "0", 
     "clog_to_syslog_facility": "daemon", 
     "osd_mon_report_interval_min": "5", 
     "filestore_max_inline_xattr_size": "0", 
     "mon_osd_down_out_subtree_limit": "rack", 
     "mon_osd_min_down_reports": "3", 
     "mon_pg_warn_min_objects": "10000", 
     "mds_session_timeout": "60", 
     "mds_bal_split_wr": "10000", 
     "mon_max_log_entries_per_event": "4096", 
     "mon_osd_min_down_reporters": "1", 
     "mon_osd_adjust_down_out_interval": "true", 
     "osd_open_classes_on_start": "true", 
     "osd_pg_stat_report_interval_max": "500", 
     "ms_die_on_bad_msg": "false", 
     "ms_inject_internal_delays": "0", 
     "mds_bal_merge_size": "50", 
     "rgw_get_obj_window_size": "16777216", 
     "osd_debug_op_order": "false", 
     "auth": "1/5", 
     "mon_max_log_epochs": "500", 
     "mon_osd_report_timeout": "900", 
     "filestore_wbthrottle_enable": "true", 
     "osd_recovery_thread_timeout": "30", 
     "mon_osd_auto_mark_in": "false", 
     "name": "mon.gravel1", 
     "osd_kill_backfill_at": "0", 
     "rbd_cache_size": "33554432", 
     "crypto": "1/5", 
     "journaler": "0/5", 
     "mon_osd_auto_mark_auto_out_in": "true", 
     "journal_max_write_entries": "100", 
     "journal_align_min_size": "65536", 
     "mon_lease": "5", 
     "rgw_swift_url": "", 
     "filestore_kill_at": "0", 
     "osd_scrub_chunk_min": "5", 
     "err_to_syslog": "false", 
     "mds": "1/5", 
     "client_mount_timeout": "300", 
     "mon_compact_on_start": "false", 
     "mon_cluster_log_to_syslog": "false", 
     "rgw_keystone_url": "", 
     "mon_client_max_log_entries_per_message": "1000", 
     "mon_leveldb_size_warn": "42949672960", 
     "osd_client_message_cap": "100", 
     "mon_cluster_log_file": "/var/log/ceph/myceph.log", 
     "mon_pg_stuck_threshold": "300", 
     "journaler_write_head_interval": "15", 
     "mds_debug_auth_pins": "false", 
     "objecter_timeout": "10", 
     "mon_sync_provider_kill_at": "0", 
     "filestore_replica_fadvise": "true", 
     "osd_data": "/var/lib/ceph/osd/myceph-gravel1", 
     "client_oc_max_dirty": "104857600", 
     "restapi_base_url": "", 
     "osd_map_cache_size": "500", 
     "auth_debug": "false", 
     "osd_recover_clone_overlap": "true", 
     "filestore_sloppy_crc_block_size": "65536", 
     "heartbeat_interval": "5", 
     "timer": "0/1", 
     "rgw_num_control_oids": "8", 
     "osd_map_dedup": "true", 
     "client_cache_mid": "0.75", 
     "ms_die_on_unhandled_msg": "false", 
     "rgw_exit_timeout_secs": "120", 
     "mon_leveldb_log": "/dev/null", 
     "osd_map_message_max": "100", 
     "fuse_allow_other": "true", 
     "mutex_perf_counter": "false", 
     "log_max_recent": "10000", 
     "mon_compact_on_bootstrap": "false", 
     "ms_tcp_nodelay": "true", 
     "mds_wipe_sessions": "false", 
     "journaler_batch_max": "0", 
     "rgw_enable_usage_log": "false", 
     "journaler_prezero_periods": "5", 
     "filestore_op_threads": "2", 
     "mds_bal_replicate_threshold": "8000", 
     "osd_leveldb_write_buffer_size": "0", 
     "rgw_enforce_swift_acls": "true", 
     "journaler_batch_interval": "0.001", 
     "osd_mon_ack_timeout": "30", 
     "fuse_default_permissions": "true", 
     "osd_debug_drop_op_probability": "0", 
     "mon_pg_warn_max_object_skew": "10", 
     "osd_max_backfills": "10", 
     "rgw_usage_log_tick_interval": "30", 
     "admin_socket": "/var/run/ceph/myceph-mon.gravel1.asok", 
     "osd_debug_drop_ping_duration": "0", 
     "max_open_files": "0", 
     "throttle": "1/1", 
     "paxos_trim_max": "500", 
     "mds_log_skip_corrupt_events": "false", 
     "mds_bal_idle_threshold": "0", 
     "ms_tcp_rcvbuf": "0", 
     "osd_journal_size": "5120", 
     "osd_op_history_duration": "600", 
     "mds_bal_unreplicate_threshold": "0", 
     "osd_remove_thread_timeout": "3600", 
     "osd_default_notify_timeout": "30", 
     "filer": "0/1", 
     "mds_beacon_interval": "4", 
     "mds_standby_for_rank": "-1", 
     "rgw_op_thread_timeout": "600", 
     "mon_slurp_bytes": "262144", 
     "ms_initial_backoff": "0.2", 
     "filestore_min_sync_interval": "0.01", 
     "osd_leveldb_log": "/dev/null", 
     "internal_safe_to_start_threads": "true", 
     "rgw_socket_path": "", 
     "mds_verify_scatter": "false", 
     "mon_health_data_update_interval": "60", 
     "filestore_inject_stall": "0", 
     "rbd_default_order": "22", 
     "mds_session_autoclose": "300", 
     "mon_debug_dump_transactions": "false", 
     "paxos_trim_min": "250", 
     "filestore_max_inline_xattr_size_xfs": "65536", 
     "mds_log_max_segments": "30", 
     "rgw_num_zone_opstate_shards": "128", 
     "client_readahead_min": "131072", 
     "osd_op_thread_timeout": "15", 
     "osd_pg_epoch_persisted_max_stale": "200", 
     "buffer": "0/1", 
     "paxos_stash_full_interval": "25", 
     "filestore_wbthrottle_xfs_bytes_start_flusher": "41943040", 
     "osd_scrub_finalize_thread_timeout": "600", 
     "client_oc_target_dirty": "8388608", 
     "osd_max_rep": "10", 
     "filestore_commit_timeout": "600", 
     "mds_bal_fragment_interval": "5", 
     "filestore_queue_committing_max_bytes": "104857600", 
     "osd_preserve_trimmed_log": "false", 
     "log_flush_on_exit": "true", 
     "osd_min_rep": "1", 
     "paxos_min_wait": "0.05", 
     "num_client": "1", 
     "rgw_log_nonexistent_bucket": "false", 
     "keyring": "/etc/ceph/myceph.mon.gravel1.keyring,/etc/ceph/myceph.keyring,/etc/ceph/keyring,/etc/ceph/keyring.bin", 
     "osd_snap_trim_thread_timeout": "3600", 
     "filestore_sloppy_crc": "false", 
     "filestore_wbthrottle_xfs_ios_start_flusher": "500", 
     "mon_sync_max_payload_size": "1048576", 
     "osd_peering_wq_batch_size": "20", 
     "log_file": "/var/log/ceph/myceph-mon.gravel1.log", 
     "mon_client_bytes": "104857600", 
     "osd_heartbeat_grace": "20", 
     "mon_pg_warn_min_pool_objects": "1000", 
     "rgw_extended_http_attrs": "", 
     "osd_max_write_size": "90", 
     "rgw_data_log_changes_size": "1000", 
     "mon_inject_sync_get_chunk_delay": "0", 
     "client_trace": "", 
     "mon_initial_members": "gravel1, gravel2, gravel3", 
     "osd_heartbeat_interval": "6", 
     "cluster_addr": ":/0", 
     "rgw_list_buckets_max_chunk": "1000", 
     "mon_compact_on_trim": "true", 
     "journal_ignore_corruption": "false", 
     "mds_log_max_events": "-1", 
     "objecter_tick_interval": "5", 
     "mds_migrator": "1/5", 
     "objclass": "0/5", 
     "rgw_admin_entry": "admin", 
     "mon_pg_warn_min_per_osd": "20", 
     "osd_min_pg_log_entries": "3000", 
     "filestore_fd_cache_size": "128", 
     "mds_bal_frag": "false", 
     "rgw_bucket_quota_soft_threshold": "0.95", 
     "osd_compact_leveldb_on_mount": "false", 
     "striper": "0/1", 
     "mon_min_osdmap_epochs": "500", 
     "mon_data_avail_crit": "5", 
     "filestore_merge_threshold": "10", 
     "mds_bal_mode": "0", 
     "mon_config_key_max_entry_size": "4096", 
     "objecter_inflight_op_bytes": "104857600", 
     "mds_bal_midchunk": "0.3", 
     "mon_osd_max_op_age": "32", 
     "mon_leveldb_paranoid": "false", 
     "mds_decay_halflife": "5", 
     "osd_failsafe_nearfull_ratio": "0.9", 
     "mon_max_osd": "10000", 
     "osd_debug_verify_stray_on_activate": "false", 
     "rgw_region_root_pool": ".rgw.root", 
     "mds_beacon_grace": "15", 
     "mds_bal_split_rd": "25000", 
     "osd_scrub_load_threshold": "0.5", 
     "rgw_bucket_quota_cache_size": "10000", 
     "osd_max_pg_log_entries": "10000", 
     "filestore_max_inline_xattr_size_other": "512", 
     "javaclient": "1/5", 
     "rgw_swift_token_expiration": "86400", 
     "client_oc": "true", 
     "filestore_op_thread_timeout": "60", 
     "log_to_stderr": "false", 
     "rgw_usage_max_shards": "32", 
     "osd_deep_scrub_stride": "524288", 
     "mon_osd_force_trim_to": "0", 
     "journal_max_write_bytes": "10485760", 
     "mds_enforce_unique_name": "true", 
     "client_snapdir": ".snap", 
     "filestore_journal_trailing": "false", 
     "mon_timecheck_interval": "300", 
     "client_debug_force_sync_read": "false", 
     "client_debug_inject_tick_delay": "0", 
     "ms_bind_port_max": "7300", 
     "mds_bal_split_bits": "3", 
     "cephx_require_signatures": "false", 
     "client_use_random_mds": "false", 
     "key": "", 
     "rgw_zone": "", 
     "mon_sync_debug_provider": "-1", 
     "run_dir": "/var/run/ceph", 
     "osd_mon_report_interval_max": "120", 
     "monc": "0/10", 
     "osd_recovery_threads": "1", 
     "journal_aio": "true", 
     "lockdep": "false", 
     "context": "0/1", 
     "mds_open_remote_link_mode": "0", 
     "cluster_network": "192.168.19.0/24", 
     "paxos": "1/5", 
     "journal_queue_max_bytes": "33554432", 
     "osd_recovery_op_warn_multiple": "16", 
     "rgw_s3_auth_use_keystone": "false", 
     "rgw_port": "", 
     "osd_leveldb_cache_size": "0", 
     "ms_inject_delay_probability": "0", 
     "public_addr": ":/0", 
     "mds_dump_cache_on_map": "false", 
     "ms_tcp_read_timeout": "900", 
     "mon_leveldb_block_size": "65536", 
     "mds_kill_import_at": "0", 
     "osd_recovery_forget_lost_objects": "false", 
     "osd_target_transaction_size": "30", 
     "mon_cluster_log_to_syslog_facility": "daemon", 
     "mon_stat_smooth_intervals": "2", 
     "mds_debug_subtrees": "false", 
     "rgw_print_continue": "true", 
     "mon_force_standby_active": "true", 
     "rgw_default_region_info_oid": "default.region", 
     "mon_sync_fs_threshold": "5", 
     "mon_osd_auto_mark_new_in": "true", 
     "client_mountpoint": "/", 
     "finisher": "1/1", 
     "rgw_data_log_obj_prefix": "data_log", 
     "mds_balancer": "1/5", 
     "osd_client_watch_timeout": "30", 
     "osd_heartbeat_min_healthy_ratio": "0.33", 
     "osd_scrub_chunk_max": "25", 
     "mds_data": "/var/lib/ceph/mds/myceph-gravel1", 
     "rgw_obj_stripe_size": "4194304", 
     "osd_pool_default_flags": "0", 
     "mds_kill_link_at": "0", 
     "ms_nocrc": "false", 
     "client_tick_interval": "1", 
     "mon_tick_interval": "5", 
     "rgw_gc_processor_period": "3600", 
     "mds_blacklist_interval": "1440", 
     "osd_client_message_size_cap": "524288000", 
     "ms_inject_delay_type": "", 
     "clog_to_syslog": "false", 
     "mds_kill_openc_at": "0", 
     "rgw_get_obj_max_req_size": "4194304", 
     "osd_auto_mark_unfound_lost": "false", 
     "ms_max_backoff": "15", 
     "cluster": "myceph", 
     "osd_recovery_max_active": "15", 
     "journal_block_align": "true", 
     "monmap": "", 
     "mds_max_file_size": "1099511627776", 
     "rgw_relaxed_s3_bucket_names": "false", 
     "heartbeat_file": "", 
     "mds_cache_mid": "0.7", 
     "mon_sync_debug": "false", 
     "mds_standby_replay": "false", 
     "mon_osd_max_split_count": "32", 
     "osd_max_attr_size": "0", 
     "filestore_wbthrottle_xfs_bytes_hard_limit": "419430400", 
     "filestore_max_inline_xattrs": "0", 
     "mds_dir_max_commit_size": "90", 
     "mds_bal_min_start": "0.2", 
     "ms_inject_socket_failures": "0", 
     "rgw_keystone_revocation_interval": "900", 
     "rbd_cache_target_dirty": "16777216", 
     "auth_service_ticket_ttl": "3600", 
     "rgw_host": "", 
     "osd_pool_default_flag_hashpspool": "false", 
     "osd_failsafe_full_ratio": "0.97", 
     "client_caps_release_delay": "5", 
     "mon_sync_debug_leader": "-1", 
     "ms_bind_ipv6": "false", 
     "client": "0/5", 
     "filestore_fail_eio": "true", 
     "mds_bal_merge_rd": "1000", 
     "mon_osd_min_up_ratio": "0.3", 
     "client_oc_size": "209715200", 
     "filestore_op_thread_suicide_timeout": "180", 
     "filestore_max_inline_xattrs_xfs": "10", 
     "osd_backfill_retry_interval": "10", 
     "mon_leveldb_write_buffer_size": "33554432", 
     "mds_bal_target_removal_max": "10", 
     "mds_bal_min_rebalance": "0.1", 
     "osd_leveldb_block_size": "0", 
     "client_oc_max_objects": "1000", 
     "mds_wipe_ino_prealloc": "false", 
     "rgw": "1/5", 
     "fuse_debug": "false", 
     "osd_recovery_max_chunk": "8388608", 
     "asok": "1/5", 
     "rgw_ops_log_socket_path": "", 
     "rbd_cache_writethrough_until_flush": "false", 
     "mon_client_ping_interval": "10", 
     "clog_to_monitors": "true", 
     "rgw_intent_log_object_name_utc": "false", 
     "mon_sync_timeout": "60", 
     "mds_thrash_exports": "0", 
     "rgw_opstate_ratelimit_sec": "30", 
     "mon": "1/5", 
     "rgw_md_log_max_shards": "64", 
     "osd_mon_heartbeat_interval": "30", 
     "fsid": "466b2ff9-970e-44a4-85d1-db0718a0c836", 
     "osd_pgp_bits": "6", 
     "osd_copyfrom_max_chunk": "8388608", 
     "mds_scatter_nudge_interval": "5", 
     "mds_debug_frag": "false", 
     "mds_log_segment_size": "0", 
     "mds_skip_ino": "0", 
     "mon_host": "192.168.18.1,192.168.18.2,192.168.18.3", 
     "osd_recovery_delay_start": "0", 
     "mon_osd_min_in_ratio": "0.3", 
     "mds_bal_need_min": "0.8", 
     "mds_thrash_fragments": "0", 
     "ms_pq_max_tokens_per_priority": "4194304", 
     "rgw_copy_obj_progress_every_bytes": "1048576", 
     "mds_bal_max": "-1", 
     "mds_kill_rename_at": "0", 
     "mon_sync_requester_kill_at": "0", 
     "osd_debug_drop_pg_create_duration": "1", 
     "mds_default_dir_hash": "2", 
     "mon_leveldb_compression": "false", 
     "rgw_copy_obj_progress": "true", 
     "osd_recovery_max_single_start": "5", 
     "rgw_zone_root_pool": ".rgw.root", 
     "filestore_max_inline_xattrs_other": "2", 
     "filestore_debug_verify_split": "false", 
     "filestore_max_sync_interval": "5", 
     "rgw_data_log_window": "30", 
     "journal_replay_from": "0", 
     "rgw_script_uri": "", 
     "rbd_cache_block_writes_upfront": "false", 
     "objecter": "0/1", 
     "heartbeatmap": "1/5", 
     "osd_command_thread_timeout": "600", 
     "journal_dio": "true", 
     "osd_uuid": "00000000-0000-0000-0000-000000000000", 
     "ms_bind_port_min": "6800", 
     "journal": "1/3", 
     "mon_delta_reset_interval": "10", 
     "host": "localhost", 
     "paxos_propose_interval": "1", 
     "filestore_wbthrottle_btrfs_inodes_start_flusher": "500", 
     "filestore_btrfs_clone_range": "true", 
     "rgw_swift_auth_entry": "auth", 
     "osd_op_log_threshold": "5", 
     "mon_osd_adjust_heartbeat_grace": "true", 
     "rbd_default_features": "3", 
     "log_max_new": "1000", 
     "paxos_service_trim_min": "250", 
     "clog_to_syslog_level": "info", 
     "mds_bal_sample_interval": "3", 
     "mon_cluster_log_to_syslog_level": "info", 
     "err_to_stderr": "true", 
     "filestore_zfs_snap": "false", 
     "filestore_max_inline_xattrs_btrfs": "10", 
     "osd_rollback_to_cluster_snap": "", 
     "rgw_cache_enabled": "true", 
     "journal_write_header_frequency": "0", 
     "rbd_default_stripe_unit": "4194304", 
     "rbd_cache": "false", 
     "filestore_journal_writeahead": "false", 
     "rgw_remote_addr_param": "REMOTE_ADDR", 
     "journal_force_aio": "false", 
     "rgw_gc_max_objs": "32", 
     "mds_standby_for_name": "", 
     "rbd_cache_max_dirty": "25165824", 
     "osd_scrub_thread_timeout": "60", 
     "filestore_index_retry_probability": "0", 
     "client_notify_timeout": "10", 
     "osd_pool_default_crush_rule": "0", 
     "rgw_s3_success_create_obj_status": "0", 
     "rbd_balance_snap_reads": "false", 
     "osd_class_dir": "/usr/lib/rados-classes", 
     "rgw_curl_wait_timeout_ms": "1000", 
     "osd_map_share_max_epochs": "100", 
     "rgw_replica_log_obj_prefix": "replica_log", 
     "mon_slurp_timeout": "10", 
     "rgw_request_uri": "", 
     "mds_client_prealloc_inos": "1000", 
     "rbd_localize_snap_reads": "false", 
     "rgw_cache_lru_size": "10000", 
     "mds_log": "true", 
     "filestore_btrfs_snap": "true", 
     "osd_pool_default_pgp_num": "8", 
     "mds_bal_interval": "10", 
     "mds_bal_target_removal_min": "5", 
     "fuse_use_invalidate_cb": "false", 
     "mds_shutdown_check": "0", 
     "mds_debug_scatterstat": "false", 
     "osd_pool_default_size": "2", 
     "client_readahead_max_bytes": "0", 
     "filestore_queue_committing_max_ops": "500", 
     "perfcounter": "1/5", 
     "mds_cache_size": "100000", 
     "filestore_wbthrottle_btrfs_bytes_hard_limit": "419430400", 
     "filestore_dump_file": "", 
     "rgw_enable_apis": "s3, swift, swift_auth, admin", 
     "ms_dispatch_throttle_bytes": "104857600", 
     "mon_osd_full_ratio": "0.95", 
     "osd_backfill_scan_min": "64", 
     "nss_db_path": "", 
     "rgw_op_thread_suicide_timeout": "0", 
     "restapi_log_level": "", 
     "mds_bal_split_size": "10000", 
     "filestore_wbthrottle_btrfs_ios_start_flusher": "500", 
     "mds_log_max_expiring": "20", 
     "public_network": "192.168.18.0/24", 
     "osd_debug_skip_full_check_in_backfill_reservation": "false", 
     "ms_pq_min_cost": "65536", 
     "rgw_usage_max_user_shards": "1", 
     "filestore_queue_max_ops": "50", 
     "rgw_region": "", 
     "optracker": "0/5", 
     "cephx_sign_messages": "true", 
     "mds_dir_commit_ratio": "0.5", 
     "osd_scrub_min_interval": "86400", 
     "mon_client_hunt_interval": "3", 
     "rgw_resolve_cname": "false", 
     "osd_client_op_priority": "63", 
     "mds_reconnect_timeout": "45", 
     "osd_leveldb_paranoid": "false", 
     "osd_deep_scrub_interval": "604800", 
     "osd_heartbeat_min_peers": "10", 
     "osd_op_threads": "2", 
     "mon_lease_renew_interval": "3", 
     "osd_crush_chooseleaf_type": "1", 
     "mds_use_tmap": "true", 
     "osd_op_complaint_time": "30", 
     "rgw_data_log_num_shards": "128", 
     "ms_die_on_old_message": "false", 
     "auth_supported": "", 
     "rgw_thread_pool_size": "100", 
     "mon_globalid_prealloc": "100", 
     "filestore_fiemap": "false"
   }

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/pg_summary
--------------------------------------------------------------------------

.. code-block:: json

   {
     "by_osd": {
       "11": {
         "active+clean": 28, 
         "creating": 11
       }, 
       "10": {
         "active+clean": 28, 
         "creating": 11
       }, 
       "1": {
         "active+clean": 24, 
         "creating": 12
       }, 
       "0": {
         "active+clean": 24, 
         "creating": 12
       }, 
       "3": {
         "active+clean": 35, 
         "creating": 10
       }, 
       "2": {
         "active+clean": 35, 
         "creating": 10
       }, 
       "5": {
         "active+clean": 35, 
         "creating": 11
       }, 
       "4": {
         "active+clean": 35, 
         "creating": 11
       }, 
       "7": {
         "active+clean": 33, 
         "creating": 11
       }, 
       "6": {
         "active+clean": 33, 
         "creating": 11
       }, 
       "9": {
         "active+clean": 37, 
         "creating": 9
       }, 
       "8": {
         "active+clean": 37, 
         "creating": 9
       }
     }, 
     "by_pool": {
       "1": {
         "active+clean": 64
       }, 
       "0": {
         "active+clean": 64
       }, 
       "3": {
         "creating": 64
       }, 
       "2": {
         "active+clean": 64
       }
     }, 
     "all": {
       "active+clean": 192, 
       "creating": 64
     }
   }

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/mon_map
-----------------------------------------------------------------------

.. code-block:: json

   {
     "quorum": [
       0, 
       1, 
       2
     ], 
     "created": "2014-09-17T14:36:05.876219", 
     "modified": "2014-09-17T14:36:05.876204", 
     "epoch": 0, 
     "mons": [
       {
         "name": "figment000", 
         "rank": 0, 
         "addr": ""
       }, 
       {
         "name": "figment001", 
         "rank": 1, 
         "addr": ""
       }, 
       {
         "name": "figment002", 
         "rank": 2, 
         "addr": ""
       }
     ], 
     "fsid": "cd50fad9-74d7-4579-9acc-f0d1e4d014b4"
   }

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/mon_status
--------------------------------------------------------------------------

.. code-block:: json

   {
     "election_epoch": 77, 
     "state": "leader", 
     "monmap": {
       "quorum": [
         0, 
         1, 
         2
       ], 
       "created": "2014-09-17T14:36:05.876219", 
       "modified": "2014-09-17T14:36:05.876204", 
       "epoch": 0, 
       "mons": [
         {
           "name": "figment000", 
           "rank": 0, 
           "addr": ""
         }, 
         {
           "name": "figment001", 
           "rank": 1, 
           "addr": ""
         }, 
         {
           "name": "figment002", 
           "rank": 2, 
           "addr": ""
         }
       ], 
       "fsid": "cd50fad9-74d7-4579-9acc-f0d1e4d014b4"
     }, 
     "rank": 0, 
     "quorum": [
       0, 
       1, 
       2
     ]
   }

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/osd_map
-----------------------------------------------------------------------

.. code-block:: json

   {
     "max_osd": 12, 
     "crush_map_text": "\n# begin crush map\ntunable choose_local_fallback_tries 5\ntunable chooseleaf_descend_once 0\ntunable choose_local_tries 2\ntunable choose_total_tries 19\n\n# devices\ndevice 0 osd.0\ndevice 1 osd.1\ndevice 2 osd.2\ndevice 3 osd.3\ndevice 4 osd.4\n\n# types\ntype 0 osd\ntype 1 host\ntype 2 rack\ntype 3 row\ntype 4 room\ntype 5 datacenter\ntype 6 root\n\n# buckets\nhost gravel3 {\n    id -4       # do not change unnecessarily\n    # weight 0.910\n    alg straw\n    hash 0  # rjenkins1\n    item osd.2 weight 0.910\n}\nhost gravel2 {\n    id -3       # do not change unnecessarily\n    # weight 0.910\n    alg straw\n    hash 0  # rjenkins1\n    item osd.1 weight 0.910\n}\nhost gravel1 {\n    id -2       # do not change unnecessarily\n    # weight 3.020\n    alg straw\n    hash 0  # rjenkins1\n    item osd.0 weight 0.910\n    item osd.3 weight 1.820\n    item osd.4 weight 0.290\n}\nroot default {\n    id -1       # do not change unnecessarily\n    # weight 4.840\n    alg straw\n    hash 0  # rjenkins1\n    item gravel1 weight 3.020\n    item gravel2 weight 0.910\n    item gravel3 weight 0.910\n}\n\n# rules\nrule data {\n    ruleset 0\n    type replicated\n    min_size 1\n    max_size 10\n    step take default\n    step chooseleaf firstn 0 type host\n    step emit\n}\nrule metadata {\n    ruleset 1\n    type replicated\n    min_size 1\n    max_size 10\n    step take default\n    step chooseleaf firstn 0 type host\n    step emit\n}\nrule rbd {\n    ruleset 2\n    type replicated\n    min_size 1\n    max_size 10\n    step take default\n    step chooseleaf firstn 0 type host\n    step emit\n}\n\n# end crush map\n", 
     "tree": {
       "nodes": [
         {
           "id": -1, 
           "type": "root", 
           "children": [
             -2, 
             -3, 
             -4
           ], 
           "name": "default", 
           "type_id": 6
         }, 
         {
           "status": "up", 
           "name": "osd.0", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 0
         }, 
         {
           "status": "up", 
           "name": "osd.1", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 1
         }, 
         {
           "status": "up", 
           "name": "osd.2", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 2
         }, 
         {
           "status": "up", 
           "name": "osd.3", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 3
         }, 
         {
           "id": -2, 
           "type": "host", 
           "children": [
             0, 
             1, 
             2, 
             3
           ], 
           "name": "figment000", 
           "type_id": 1
         }, 
         {
           "status": "up", 
           "name": "osd.8", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 8
         }, 
         {
           "status": "up", 
           "name": "osd.9", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 9
         }, 
         {
           "status": "up", 
           "name": "osd.10", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 10
         }, 
         {
           "status": "up", 
           "name": "osd.11", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 11
         }, 
         {
           "id": -3, 
           "type": "host", 
           "children": [
             8, 
             9, 
             10, 
             11
           ], 
           "name": "figment002", 
           "type_id": 1
         }, 
         {
           "status": "up", 
           "name": "osd.4", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 4
         }, 
         {
           "status": "up", 
           "name": "osd.5", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 5
         }, 
         {
           "status": "up", 
           "name": "osd.6", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 6
         }, 
         {
           "status": "up", 
           "name": "osd.7", 
           "exists": 1, 
           "type_id": 0, 
           "reweight": 1.0, 
           "crush_weight": 1.0, 
           "depth": 2, 
           "type": "osd", 
           "id": 7
         }, 
         {
           "id": -4, 
           "type": "host", 
           "children": [
             4, 
             5, 
             6, 
             7
           ], 
           "name": "figment001", 
           "type_id": 1
         }
       ]
     }, 
     "osds": [
       {
         "down_at": 0, 
         "uuid": "2c2f9ae3-acc2-4f14-86ef-3e181090bbb5", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 0
       }, 
       {
         "down_at": 0, 
         "uuid": "566c503c-e64f-45c2-a9ca-3d07ee4145ed", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 1
       }, 
       {
         "down_at": 0, 
         "uuid": "5cd83218-03c2-4c44-a7e0-ba90584cbd78", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 2
       }, 
       {
         "down_at": 0, 
         "uuid": "60fe60d9-8eee-4c8e-aa5d-051ea8bdc97b", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 3
       }, 
       {
         "down_at": 0, 
         "uuid": "331cad3c-2ad7-4acb-b3a8-41eee20e8e46", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 4
       }, 
       {
         "down_at": 0, 
         "uuid": "2d2dcccc-2505-4acb-89a8-16402ffef117", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 5
       }, 
       {
         "down_at": 0, 
         "uuid": "d593f943-05a5-4238-a087-629f2273334a", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 6
       }, 
       {
         "down_at": 0, 
         "uuid": "2a5ca0e4-c3cc-4219-b096-d4fec9d2c849", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 7
       }, 
       {
         "down_at": 0, 
         "uuid": "ea092b0f-e55b-4d0e-9e91-3a8915112069", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 8
       }, 
       {
         "down_at": 0, 
         "uuid": "2cd4057c-5250-43f0-95ea-08c2c8b8fbb3", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 9
       }, 
       {
         "down_at": 0, 
         "uuid": "46b00e42-a4e4-4a8d-94fc-feccc84bdbbe", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 10
       }, 
       {
         "down_at": 0, 
         "uuid": "cfae2632-6b99-4bb8-a269-ef862af948fa", 
         "heartbeat_front_addr": "", 
         "heartbeat_back_addr": "", 
         "lost_at": 0, 
         "up": 1, 
         "up_from": 0, 
         "state": [
           "exists", 
           "up"
         ], 
         "last_clean_begin": 0, 
         "last_clean_end": 0, 
         "in": 1, 
         "public_addr": "", 
         "up_thru": 0, 
         "cluster_addr": "", 
         "osd": 11
       }
     ], 
     "crush": {
       "rules": [
         {
           "min_size": 1, 
           "rule_name": "data", 
           "steps": [
             {
               "item": -1, 
               "op": "take"
             }, 
             {
               "num": 0, 
               "type": "host", 
               "op": "chooseleaf_firstn"
             }, 
             {
               "op": "emit"
             }
           ], 
           "ruleset": 0, 
           "type": 1, 
           "rule_id": 0, 
           "max_size": 10
         }, 
         {
           "min_size": 1, 
           "rule_name": "metadata", 
           "steps": [
             {
               "item": -1, 
               "op": "take"
             }, 
             {
               "num": 0, 
               "type": "host", 
               "op": "chooseleaf_firstn"
             }, 
             {
               "op": "emit"
             }
           ], 
           "ruleset": 1, 
           "type": 1, 
           "rule_id": 1, 
           "max_size": 10
         }, 
         {
           "min_size": 1, 
           "rule_name": "rbd", 
           "steps": [
             {
               "item": -1, 
               "op": "take"
             }, 
             {
               "num": 0, 
               "type": "host", 
               "op": "chooseleaf_firstn"
             }, 
             {
               "op": "emit"
             }
           ], 
           "ruleset": 2, 
           "type": 1, 
           "rule_id": 2, 
           "max_size": 10
         }
       ], 
       "tunables": {
         "choose_local_fallback_tries": 5, 
         "chooseleaf_descend_once": 0, 
         "choose_total_tries": 19, 
         "choose_local_tries": 2
       }, 
       "buckets": [
         {
           "hash": "rjenkins1", 
           "name": "default", 
           "weight": 317191, 
           "type_id": 6, 
           "alg": "straw", 
           "type_name": "root", 
           "items": [
             {
               "id": -2, 
               "weight": 197917, 
               "pos": 0
             }, 
             {
               "id": -3, 
               "weight": 59637, 
               "pos": 1
             }, 
             {
               "id": -4, 
               "weight": 59637, 
               "pos": 2
             }
           ], 
           "id": -1
         }, 
         {
           "hash": "rjenkins1", 
           "name": "gravel1", 
           "weight": 197917, 
           "type_id": 1, 
           "alg": "straw", 
           "type_name": "host", 
           "items": [
             {
               "id": 0, 
               "weight": 59637, 
               "pos": 0
             }, 
             {
               "id": 3, 
               "weight": 119275, 
               "pos": 1
             }, 
             {
               "id": 4, 
               "weight": 19005, 
               "pos": 2
             }
           ], 
           "id": -2
         }, 
         {
           "hash": "rjenkins1", 
           "name": "gravel2", 
           "weight": 59637, 
           "type_id": 1, 
           "alg": "straw", 
           "type_name": "host", 
           "items": [
             {
               "id": 1, 
               "weight": 59637, 
               "pos": 0
             }
           ], 
           "id": -3
         }, 
         {
           "hash": "rjenkins1", 
           "name": "gravel3", 
           "weight": 59637, 
           "type_id": 1, 
           "alg": "straw", 
           "type_name": "host", 
           "items": [
             {
               "id": 2, 
               "weight": 59637, 
               "pos": 0
             }
           ], 
           "id": -4
         }
       ], 
       "devices": [
         {
           "id": 0, 
           "name": "osd.0"
         }, 
         {
           "id": 1, 
           "name": "osd.1"
         }, 
         {
           "id": 2, 
           "name": "osd.2"
         }, 
         {
           "id": 3, 
           "name": "osd.3"
         }, 
         {
           "id": 4, 
           "name": "osd.4"
         }
       ], 
       "types": [
         {
           "name": "osd", 
           "type_id": 0
         }, 
         {
           "name": "host", 
           "type_id": 1
         }, 
         {
           "name": "rack", 
           "type_id": 2
         }, 
         {
           "name": "row", 
           "type_id": 3
         }, 
         {
           "name": "room", 
           "type_id": 4
         }, 
         {
           "name": "datacenter", 
           "type_id": 5
         }, 
         {
           "name": "root", 
           "type_id": 6
         }
       ]
     }, 
     "epoch": 2, 
     "flags": "", 
     "pools": [
       {
         "flags_names": "", 
         "tier_of": -1, 
         "pg_placement_num": 64, 
         "quota_max_bytes": 0, 
         "size": 2, 
         "snap_seq": 0, 
         "auid": 0, 
         "pg_num": 64, 
         "type": 1, 
         "crush_ruleset": 2, 
         "pool_name": "data", 
         "snap_mode": "selfmanaged", 
         "tiers": [], 
         "min_size": 1, 
         "crash_replay_interval": 0, 
         "object_hash": 2, 
         "write_tier": -1, 
         "properties": [], 
         "pool": 0, 
         "removed_snaps": "[]", 
         "cache_mode": "none", 
         "pool_snaps": {}, 
         "quota_max_objects": 0, 
         "flags": 0, 
         "snap_epoch": 0, 
         "last_change": "1", 
         "read_tier": -1
       }, 
       {
         "flags_names": "", 
         "tier_of": -1, 
         "pg_placement_num": 64, 
         "quota_max_bytes": 0, 
         "size": 2, 
         "snap_seq": 0, 
         "auid": 0, 
         "pg_num": 64, 
         "type": 1, 
         "crush_ruleset": 2, 
         "pool_name": "metadata", 
         "snap_mode": "selfmanaged", 
         "tiers": [], 
         "min_size": 1, 
         "crash_replay_interval": 0, 
         "object_hash": 2, 
         "write_tier": -1, 
         "properties": [], 
         "pool": 1, 
         "removed_snaps": "[]", 
         "cache_mode": "none", 
         "pool_snaps": {}, 
         "quota_max_objects": 0, 
         "flags": 0, 
         "snap_epoch": 0, 
         "last_change": "1", 
         "read_tier": -1
       }, 
       {
         "flags_names": "", 
         "tier_of": -1, 
         "pg_placement_num": 64, 
         "quota_max_bytes": 0, 
         "size": 2, 
         "snap_seq": 0, 
         "auid": 0, 
         "pg_num": 64, 
         "type": 1, 
         "crush_ruleset": 2, 
         "pool_name": "rbd", 
         "snap_mode": "selfmanaged", 
         "tiers": [], 
         "min_size": 1, 
         "crash_replay_interval": 0, 
         "object_hash": 2, 
         "write_tier": -1, 
         "properties": [], 
         "pool": 2, 
         "removed_snaps": "[]", 
         "cache_mode": "none", 
         "pool_snaps": {}, 
         "quota_max_objects": 0, 
         "flags": 0, 
         "snap_epoch": 0, 
         "last_change": "1", 
         "read_tier": -1
       }, 
       {
         "flags_names": "", 
         "tier_of": -1, 
         "pg_placement_num": 64, 
         "quota_max_bytes": 0, 
         "size": 2, 
         "snap_seq": 0, 
         "auid": 0, 
         "pg_num": 64, 
         "type": 1, 
         "crush_ruleset": 2, 
         "pool_name": "newname", 
         "snap_mode": "selfmanaged", 
         "tiers": [], 
         "min_size": 1, 
         "crash_replay_interval": 0, 
         "object_hash": 2, 
         "write_tier": -1, 
         "properties": [], 
         "pool": 3, 
         "removed_snaps": "[]", 
         "cache_mode": "none", 
         "pool_snaps": {}, 
         "quota_max_objects": 0, 
         "flags": 0, 
         "snap_epoch": 0, 
         "last_change": "1", 
         "read_tier": -1
       }
     ], 
     "fsid": "cd50fad9-74d7-4579-9acc-f0d1e4d014b4"
   }

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/health
----------------------------------------------------------------------

.. code-block:: json

   {
     "overall_status": "HEALTH_OK", 
     "health": {
       "health_services": []
     }, 
     "detail": [], 
     "timechecks": {}, 
     "summary": []
   }

api/v2/cluster/cd50fad9-74d7-4579-9acc-f0d1e4d014b4/sync_object/mds_map
-----------------------------------------------------------------------

.. code-block:: json

   {
     "info": {}, 
     "up": {}, 
     "max_mds": 1, 
     "in": []
   }

