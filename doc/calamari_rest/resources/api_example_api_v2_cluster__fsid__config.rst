Examples for api/v2/cluster/<fsid>/config
=========================================

api/v2/cluster/dce20d46-f010-4883-988c-4a6d8bd15793/config
----------------------------------------------------------

.. code-block:: json

   [
     {
       "value": "43200", 
       "key": "auth_mon_ticket_ttl"
     }, 
     {
       "value": "0", 
       "key": "journal_replay_from"
     }, 
     {
       "value": "1", 
       "key": "ms_inject_delay_max"
     }, 
     {
       "value": "", 
       "key": "rgw_swift_auth_url"
     }, 
     {
       "value": "1/5", 
       "key": "mds_log_expire"
     }, 
     {
       "value": "false", 
       "key": "osd_debug_pg_log_writeout"
     }, 
     {
       "value": "500", 
       "key": "filestore_wbthrottle_xfs_inodes_start_flusher"
     }, 
     {
       "value": "1", 
       "key": "rbd_default_stripe_count"
     }, 
     {
       "value": "0.3", 
       "key": "mon_osd_laggy_weight"
     }, 
     {
       "value": "500", 
       "key": "mon_max_pgmap_epochs"
     }, 
     {
       "value": "0/5", 
       "key": "osd"
     }, 
     {
       "value": "10", 
       "key": "mon_accept_timeout"
     }, 
     {
       "value": "419430400", 
       "key": "mon_daemon_bytes"
     }, 
     {
       "value": "16384", 
       "key": "client_cache_size"
     }, 
     {
       "value": "10", 
       "key": "rbd_concurrent_management_ops"
     }, 
     {
       "value": "false", 
       "key": "osd_use_stale_snap"
     }, 
     {
       "value": "0/5", 
       "key": "tp"
     }, 
     {
       "value": "cephx", 
       "key": "auth_client_required"
     }, 
     {
       "value": "3600", 
       "key": "rgw_gc_processor_max_time"
     }, 
     {
       "value": "4", 
       "key": "client_readahead_max_periods"
     }, 
     {
       "value": "2", 
       "key": "mon_probe_timeout"
     }, 
     {
       "value": "256", 
       "key": "osd_command_max_records"
     }, 
     {
       "value": "3600", 
       "key": "mon_osd_laggy_halflife"
     }, 
     {
       "value": "", 
       "key": "rgw_keystone_admin_token"
     }, 
     {
       "value": "10", 
       "key": "osd_recover_clone_overlap_limit"
     }, 
     {
       "value": "5", 
       "key": "client_oc_max_dirty_age"
     }, 
     {
       "value": "swift", 
       "key": "rgw_swift_url_prefix"
     }, 
     {
       "value": "/var/log/ceph/myceph-mon.gravel1.tdump", 
       "key": "mon_debug_dump_location"
     }, 
     {
       "value": "false", 
       "key": "cephx_service_require_signatures"
     }, 
     {
       "value": "300", 
       "key": "mon_subscribe_interval"
     }, 
     {
       "value": "10", 
       "key": "paxos_max_join_drift"
     }, 
     {
       "value": "7200", 
       "key": "rgw_gc_obj_min_wait"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_journal_replay_at"
     }, 
     {
       "value": "1/5", 
       "key": "mds_locker"
     }, 
     {
       "value": "false", 
       "key": "filestore_debug_inject_read_err"
     }, 
     {
       "value": "10000", 
       "key": "mds_bal_split_wr"
     }, 
     {
       "value": "104857600", 
       "key": "filestore_queue_max_bytes"
     }, 
     {
       "value": "%Y-%m-%d-%H-%i-%n", 
       "key": "rgw_log_object_name"
     }, 
     {
       "value": "0.8", 
       "key": "osd_age"
     }, 
     {
       "value": "192.168.18.0/24", 
       "key": "public_network"
     }, 
     {
       "value": "45", 
       "key": "osd_default_data_pool_replay_window"
     }, 
     {
       "value": "0", 
       "key": "osd_pool_default_min_size"
     }, 
     {
       "value": "1000", 
       "key": "filestore_update_to"
     }, 
     {
       "value": "1.2", 
       "key": "mds_bal_need_max"
     }, 
     {
       "value": "true", 
       "key": "osd_leveldb_compression"
     }, 
     {
       "value": "1048576", 
       "key": "mds_mem_max"
     }, 
     {
       "value": "5000", 
       "key": "filestore_wbthrottle_btrfs_ios_hard_limit"
     }, 
     {
       "value": "1024", 
       "key": "osd_max_pgls"
     }, 
     {
       "value": "0/1", 
       "key": "context"
     }, 
     {
       "value": "false", 
       "key": "filestore_fsync_flushes_journal_data"
     }, 
     {
       "value": "0/5", 
       "key": "objectcacher"
     }, 
     {
       "value": "10", 
       "key": "osd_recovery_op_priority"
     }, 
     {
       "value": "false", 
       "key": "mds_dump_cache_after_rejoin"
     }, 
     {
       "value": "41943040", 
       "key": "filestore_wbthrottle_btrfs_bytes_start_flusher"
     }, 
     {
       "value": "0.05", 
       "key": "mon_clock_drift_allowed"
     }, 
     {
       "value": "300", 
       "key": "rgw_init_timeout"
     }, 
     {
       "value": "false", 
       "key": "osd_verify_sparse_read_holes"
     }, 
     {
       "value": "1", 
       "key": "mds_replay_interval"
     }, 
     {
       "value": "0", 
       "key": "mon_leveldb_max_open_files"
     }, 
     {
       "value": "1", 
       "key": "osd_max_scrubs"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_journal_at"
     }, 
     {
       "value": "0", 
       "key": "osd_leveldb_max_open_files"
     }, 
     {
       "value": "false", 
       "key": "log_to_syslog"
     }, 
     {
       "value": "true", 
       "key": "mon_compact_on_trim"
     }, 
     {
       "value": "false", 
       "key": "osd_debug_verify_snaps_on_info"
     }, 
     {
       "value": "false", 
       "key": "filestore_blackhole"
     }, 
     {
       "value": "0", 
       "key": "paxos_kill_at"
     }, 
     {
       "value": "10", 
       "key": "osd_max_push_objects"
     }, 
     {
       "value": "%Y-%m-%d-%i-%n", 
       "key": "rgw_intent_log_object_name"
     }, 
     {
       "value": ":/0", 
       "key": "osd_heartbeat_addr"
     }, 
     {
       "value": "300", 
       "key": "mon_osd_down_out_interval"
     }, 
     {
       "value": "600", 
       "key": "rgw_bucket_quota_ttl"
     }, 
     {
       "value": "true", 
       "key": "fatal_signal_handlers"
     }, 
     {
       "value": "1000", 
       "key": "mds_bal_merge_wr"
     }, 
     {
       "value": "6", 
       "key": "osd_pg_bits"
     }, 
     {
       "value": "500", 
       "key": "paxos_service_trim_max"
     }, 
     {
       "value": "3600", 
       "key": "rgw_gc_processor_period"
     }, 
     {
       "value": "30", 
       "key": "mon_pg_create_interval"
     }, 
     {
       "value": "false", 
       "key": "filestore_debug_omap_check"
     }, 
     {
       "value": "true", 
       "key": "rgw_ops_log_rados"
     }, 
     {
       "value": "20", 
       "key": "osd_op_history_size"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_journal_expire_at"
     }, 
     {
       "value": "false", 
       "key": "daemonize"
     }, 
     {
       "value": "1", 
       "key": "rbd_default_format"
     }, 
     {
       "value": "0", 
       "key": "osd_age_time"
     }, 
     {
       "value": "10000", 
       "key": "rgw_keystone_token_cache_size"
     }, 
     {
       "value": "0.001", 
       "key": "mds_bal_minchunk"
     }, 
     {
       "value": "5000", 
       "key": "filestore_wbthrottle_xfs_inodes_hard_limit"
     }, 
     {
       "value": "2", 
       "key": "filestore_split_multiple"
     }, 
     {
       "value": "/etc/mime.types", 
       "key": "rgw_mime_types_file"
     }, 
     {
       "value": "1", 
       "key": "osd_disk_threads"
     }, 
     {
       "value": "0.85", 
       "key": "mon_osd_nearfull_ratio"
     }, 
     {
       "value": "1024", 
       "key": "objecter_inflight_ops"
     }, 
     {
       "value": "5", 
       "key": "osd_mon_shutdown_timeout"
     }, 
     {
       "value": "5242880", 
       "key": "rgw_ops_log_data_backlog"
     }, 
     {
       "value": "true", 
       "key": "perf"
     }, 
     {
       "value": "2048", 
       "key": "filestore_max_inline_xattr_size_btrfs"
     }, 
     {
       "value": "false", 
       "key": "osd_check_for_log_corruption"
     }, 
     {
       "value": "false", 
       "key": "osd_auto_weight"
     }, 
     {
       "value": "Member, admin", 
       "key": "rgw_keystone_accepted_roles"
     }, 
     {
       "value": "300", 
       "key": "journal_queue_max_ops"
     }, 
     {
       "value": "", 
       "key": "pid_file"
     }, 
     {
       "value": "1000", 
       "key": "osd_push_per_object_cost"
     }, 
     {
       "value": "1", 
       "key": "max_mds"
     }, 
     {
       "value": "false", 
       "key": "cephx_cluster_require_signatures"
     }, 
     {
       "value": "true", 
       "key": "rgw_s3_auth_use_rados"
     }, 
     {
       "value": "false", 
       "key": "ms_nocrc"
     }, 
     {
       "value": "65536", 
       "key": "mon_max_pool_pg_num"
     }, 
     {
       "value": "info", 
       "key": "mon_cluster_log_file_level"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_export_at"
     }, 
     {
       "value": "1", 
       "key": "rbd_cache_max_dirty_age"
     }, 
     {
       "value": "0", 
       "key": "mds_inject_traceless_reply_probability"
     }, 
     {
       "value": "0/5", 
       "key": "none"
     }, 
     {
       "value": "/", 
       "key": "chdir"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_mdstable_at"
     }, 
     {
       "value": "0", 
       "key": "mon_leveldb_bloom_size"
     }, 
     {
       "value": "", 
       "key": "rgw_dns_name"
     }, 
     {
       "value": "8", 
       "key": "osd_pool_default_pg_num"
     }, 
     {
       "value": "0/5", 
       "key": "rados"
     }, 
     {
       "value": "0/5", 
       "key": "ms"
     }, 
     {
       "value": "/var/lib/ceph/mon/myceph-gravel1", 
       "key": "mon_data"
     }, 
     {
       "value": "false", 
       "key": "filestore_journal_parallel"
     }, 
     {
       "value": "10", 
       "key": "journaler_prefetch_periods"
     }, 
     {
       "value": "0", 
       "key": "clock_offset"
     }, 
     {
       "value": "30", 
       "key": "mon_data_avail_warn"
     }, 
     {
       "value": "true", 
       "key": "fuse_big_writes"
     }, 
     {
       "value": "false", 
       "key": "inject_early_sigterm"
     }, 
     {
       "value": "512", 
       "key": "osd_backfill_scan_max"
     }, 
     {
       "value": "false", 
       "key": "rgw_log_object_name_utc"
     }, 
     {
       "value": "10485760", 
       "key": "journal_max_corrupt_search"
     }, 
     {
       "value": "5000", 
       "key": "filestore_wbthrottle_btrfs_inodes_hard_limit"
     }, 
     {
       "value": "5000", 
       "key": "filestore_wbthrottle_xfs_ios_hard_limit"
     }, 
     {
       "value": "0", 
       "key": "heartbeat_inject_failure"
     }, 
     {
       "value": "0", 
       "key": "mon_pool_quota_warn_threshold"
     }, 
     {
       "value": "-1", 
       "key": "mds_bal_max_until"
     }, 
     {
       "value": "10", 
       "key": "mon_lease_ack_timeout"
     }, 
     {
       "value": "1048576", 
       "key": "ms_rwthread_stack_bytes"
     }, 
     {
       "value": "65536", 
       "key": "osd_op_pq_min_cost"
     }, 
     {
       "value": "true", 
       "key": "mds_early_reply"
     }, 
     {
       "value": "0/5", 
       "key": "journaler"
     }, 
     {
       "value": "/var/lib/ceph/radosgw/myceph-gravel1", 
       "key": "rgw_data"
     }, 
     {
       "value": "-1", 
       "key": "mon_sync_debug_provider_fallback"
     }, 
     {
       "value": "500", 
       "key": "paxos_min"
     }, 
     {
       "value": "536870912", 
       "key": "mon_leveldb_cache_size"
     }, 
     {
       "value": "false", 
       "key": "filestore"
     }, 
     {
       "value": "8388608", 
       "key": "osd_max_push_cost"
     }, 
     {
       "value": "100", 
       "key": "osd_scan_list_ping_tp_interval"
     }, 
     {
       "value": "/var/lib/ceph/osd/myceph-gravel1/journal", 
       "key": "osd_journal"
     }, 
     {
       "value": "false", 
       "key": "journal_zero_on_create"
     }, 
     {
       "value": "4194304", 
       "key": "osd_op_pq_max_tokens_per_priority"
     }, 
     {
       "value": "1", 
       "key": "mds_dirstat_min_interval"
     }, 
     {
       "value": "4096", 
       "key": "filestore_fiemap_threshold"
     }, 
     {
       "value": "0", 
       "key": "osd_debug_drop_ping_probability"
     }, 
     {
       "value": "", 
       "key": "keyfile"
     }, 
     {
       "value": "0", 
       "key": "osd_debug_drop_pg_create_probability"
     }, 
     {
       "value": "0.97", 
       "key": "log_stop_at_utilization"
     }, 
     {
       "value": "true", 
       "key": "journaler_allow_split_entries"
     }, 
     {
       "value": "604800", 
       "key": "osd_scrub_max_interval"
     }, 
     {
       "value": "cephx", 
       "key": "auth_cluster_required"
     }, 
     {
       "value": "0", 
       "key": "osd_leveldb_bloom_size"
     }, 
     {
       "value": "true", 
       "key": "fuse_atomic_o_trunc"
     }, 
     {
       "value": "0", 
       "key": "mon_pool_quota_crit_threshold"
     }, 
     {
       "value": "daemon", 
       "key": "clog_to_syslog_facility"
     }, 
     {
       "value": "5", 
       "key": "osd_mon_report_interval_min"
     }, 
     {
       "value": "0", 
       "key": "filestore_max_inline_xattr_size"
     }, 
     {
       "value": "rack", 
       "key": "mon_osd_down_out_subtree_limit"
     }, 
     {
       "value": "3", 
       "key": "mon_osd_min_down_reports"
     }, 
     {
       "value": "false", 
       "key": "mutex_perf_counter"
     }, 
     {
       "value": "60", 
       "key": "mds_session_timeout"
     }, 
     {
       "value": "5", 
       "key": "mon_clock_drift_warn_backoff"
     }, 
     {
       "value": "4096", 
       "key": "mon_max_log_entries_per_event"
     }, 
     {
       "value": "1", 
       "key": "mon_osd_min_down_reporters"
     }, 
     {
       "value": "true", 
       "key": "mon_osd_adjust_down_out_interval"
     }, 
     {
       "value": "false", 
       "key": "rgw_relaxed_s3_bucket_names"
     }, 
     {
       "value": "500", 
       "key": "osd_pg_stat_report_interval_max"
     }, 
     {
       "value": "false", 
       "key": "ms_die_on_bad_msg"
     }, 
     {
       "value": "0", 
       "key": "ms_inject_internal_delays"
     }, 
     {
       "value": "50", 
       "key": "mds_bal_merge_size"
     }, 
     {
       "value": "16777216", 
       "key": "rgw_get_obj_window_size"
     }, 
     {
       "value": "false", 
       "key": "osd_debug_op_order"
     }, 
     {
       "value": "1/5", 
       "key": "auth"
     }, 
     {
       "value": "500", 
       "key": "mon_max_log_epochs"
     }, 
     {
       "value": "900", 
       "key": "mon_osd_report_timeout"
     }, 
     {
       "value": "true", 
       "key": "filestore_wbthrottle_enable"
     }, 
     {
       "value": "30", 
       "key": "osd_recovery_thread_timeout"
     }, 
     {
       "value": "0.7", 
       "key": "mds_cache_mid"
     }, 
     {
       "value": "mon.gravel1", 
       "key": "name"
     }, 
     {
       "value": "0", 
       "key": "osd_kill_backfill_at"
     }, 
     {
       "value": "33554432", 
       "key": "rbd_cache_size"
     }, 
     {
       "value": "1/5", 
       "key": "crypto"
     }, 
     {
       "value": "1024", 
       "key": "rgw_usage_log_flush_threshold"
     }, 
     {
       "value": "true", 
       "key": "mon_osd_auto_mark_auto_out_in"
     }, 
     {
       "value": "100", 
       "key": "journal_max_write_entries"
     }, 
     {
       "value": "65536", 
       "key": "journal_align_min_size"
     }, 
     {
       "value": "5", 
       "key": "mon_lease"
     }, 
     {
       "value": "", 
       "key": "rgw_swift_url"
     }, 
     {
       "value": "0", 
       "key": "filestore_kill_at"
     }, 
     {
       "value": "5", 
       "key": "osd_scrub_chunk_min"
     }, 
     {
       "value": "30", 
       "key": "rgw_data_log_window"
     }, 
     {
       "value": "1/5", 
       "key": "mds"
     }, 
     {
       "value": "300", 
       "key": "client_mount_timeout"
     }, 
     {
       "value": "false", 
       "key": "mon_compact_on_start"
     }, 
     {
       "value": "false", 
       "key": "mon_cluster_log_to_syslog"
     }, 
     {
       "value": "", 
       "key": "rgw_keystone_url"
     }, 
     {
       "value": "1000", 
       "key": "mon_client_max_log_entries_per_message"
     }, 
     {
       "value": "42949672960", 
       "key": "mon_leveldb_size_warn"
     }, 
     {
       "value": "100", 
       "key": "osd_client_message_cap"
     }, 
     {
       "value": "/var/log/ceph/myceph.log", 
       "key": "mon_cluster_log_file"
     }, 
     {
       "value": "300", 
       "key": "mon_pg_stuck_threshold"
     }, 
     {
       "value": "15", 
       "key": "journaler_write_head_interval"
     }, 
     {
       "value": "false", 
       "key": "mds_debug_auth_pins"
     }, 
     {
       "value": "10", 
       "key": "objecter_timeout"
     }, 
     {
       "value": "0", 
       "key": "mon_sync_provider_kill_at"
     }, 
     {
       "value": "true", 
       "key": "filestore_replica_fadvise"
     }, 
     {
       "value": "/var/lib/ceph/osd/myceph-gravel1", 
       "key": "osd_data"
     }, 
     {
       "value": "104857600", 
       "key": "client_oc_max_dirty"
     }, 
     {
       "value": "", 
       "key": "restapi_base_url"
     }, 
     {
       "value": "419430400", 
       "key": "filestore_wbthrottle_xfs_bytes_hard_limit"
     }, 
     {
       "value": "false", 
       "key": "auth_debug"
     }, 
     {
       "value": "true", 
       "key": "osd_recover_clone_overlap"
     }, 
     {
       "value": "65536", 
       "key": "filestore_sloppy_crc_block_size"
     }, 
     {
       "value": "0", 
       "key": "filestore_max_inline_xattrs"
     }, 
     {
       "value": "0/1", 
       "key": "timer"
     }, 
     {
       "value": "8", 
       "key": "rgw_num_control_oids"
     }, 
     {
       "value": "true", 
       "key": "osd_map_dedup"
     }, 
     {
       "value": "0.75", 
       "key": "client_cache_mid"
     }, 
     {
       "value": "false", 
       "key": "ms_die_on_unhandled_msg"
     }, 
     {
       "value": "120", 
       "key": "rgw_exit_timeout_secs"
     }, 
     {
       "value": "/dev/null", 
       "key": "mon_leveldb_log"
     }, 
     {
       "value": "100", 
       "key": "osd_map_message_max"
     }, 
     {
       "value": "true", 
       "key": "fuse_allow_other"
     }, 
     {
       "value": "10000", 
       "key": "mon_pg_warn_min_objects"
     }, 
     {
       "value": "10000", 
       "key": "log_max_recent"
     }, 
     {
       "value": "true", 
       "key": "journal_aio"
     }, 
     {
       "value": "false", 
       "key": "mon_compact_on_bootstrap"
     }, 
     {
       "value": "true", 
       "key": "ms_tcp_nodelay"
     }, 
     {
       "value": "false", 
       "key": "mds_wipe_sessions"
     }, 
     {
       "value": "0", 
       "key": "journaler_batch_max"
     }, 
     {
       "value": "false", 
       "key": "rgw_enable_usage_log"
     }, 
     {
       "value": "5", 
       "key": "journaler_prezero_periods"
     }, 
     {
       "value": "2", 
       "key": "filestore_op_threads"
     }, 
     {
       "value": "8000", 
       "key": "mds_bal_replicate_threshold"
     }, 
     {
       "value": "0", 
       "key": "osd_leveldb_write_buffer_size"
     }, 
     {
       "value": "0", 
       "key": "rgw_s3_success_create_obj_status"
     }, 
     {
       "value": "0.001", 
       "key": "journaler_batch_interval"
     }, 
     {
       "value": "30", 
       "key": "osd_mon_ack_timeout"
     }, 
     {
       "value": "true", 
       "key": "fuse_default_permissions"
     }, 
     {
       "value": "0", 
       "key": "osd_debug_drop_op_probability"
     }, 
     {
       "value": "10", 
       "key": "mon_pg_warn_max_object_skew"
     }, 
     {
       "value": "10", 
       "key": "osd_max_backfills"
     }, 
     {
       "value": "30", 
       "key": "rgw_usage_log_tick_interval"
     }, 
     {
       "value": "/var/run/ceph/myceph-mon.gravel1.asok", 
       "key": "admin_socket"
     }, 
     {
       "value": "0", 
       "key": "osd_debug_drop_ping_duration"
     }, 
     {
       "value": "false", 
       "key": "journal_ignore_corruption"
     }, 
     {
       "value": "1/1", 
       "key": "throttle"
     }, 
     {
       "value": "500", 
       "key": "paxos_trim_max"
     }, 
     {
       "value": "false", 
       "key": "mds_log_skip_corrupt_events"
     }, 
     {
       "value": "", 
       "key": "rgw_host"
     }, 
     {
       "value": "0", 
       "key": "ms_tcp_rcvbuf"
     }, 
     {
       "value": "5120", 
       "key": "osd_journal_size"
     }, 
     {
       "value": "600", 
       "key": "osd_op_history_duration"
     }, 
     {
       "value": "0", 
       "key": "mds_bal_unreplicate_threshold"
     }, 
     {
       "value": "3600", 
       "key": "osd_remove_thread_timeout"
     }, 
     {
       "value": "30", 
       "key": "osd_default_notify_timeout"
     }, 
     {
       "value": "replica_log", 
       "key": "rgw_replica_log_obj_prefix"
     }, 
     {
       "value": "4", 
       "key": "mds_beacon_interval"
     }, 
     {
       "value": "600", 
       "key": "rgw_op_thread_timeout"
     }, 
     {
       "value": "512", 
       "key": "filestore_max_inline_xattr_size_other"
     }, 
     {
       "value": "0.2", 
       "key": "ms_initial_backoff"
     }, 
     {
       "value": "0.01", 
       "key": "filestore_min_sync_interval"
     }, 
     {
       "value": "/dev/null", 
       "key": "osd_leveldb_log"
     }, 
     {
       "value": "true", 
       "key": "internal_safe_to_start_threads"
     }, 
     {
       "value": "", 
       "key": "rgw_socket_path"
     }, 
     {
       "value": "false", 
       "key": "mds_verify_scatter"
     }, 
     {
       "value": "60", 
       "key": "mon_health_data_update_interval"
     }, 
     {
       "value": "0", 
       "key": "filestore_inject_stall"
     }, 
     {
       "value": "22", 
       "key": "rbd_default_order"
     }, 
     {
       "value": "300", 
       "key": "mds_session_autoclose"
     }, 
     {
       "value": "false", 
       "key": "mon_debug_dump_transactions"
     }, 
     {
       "value": "250", 
       "key": "paxos_trim_min"
     }, 
     {
       "value": "65536", 
       "key": "filestore_max_inline_xattr_size_xfs"
     }, 
     {
       "value": "30", 
       "key": "mds_log_max_segments"
     }, 
     {
       "value": "128", 
       "key": "rgw_num_zone_opstate_shards"
     }, 
     {
       "value": "131072", 
       "key": "client_readahead_min"
     }, 
     {
       "value": "15", 
       "key": "osd_op_thread_timeout"
     }, 
     {
       "value": "200", 
       "key": "osd_pg_epoch_persisted_max_stale"
     }, 
     {
       "value": "0/1", 
       "key": "buffer"
     }, 
     {
       "value": "25", 
       "key": "paxos_stash_full_interval"
     }, 
     {
       "value": "41943040", 
       "key": "filestore_wbthrottle_xfs_bytes_start_flusher"
     }, 
     {
       "value": "600", 
       "key": "osd_scrub_finalize_thread_timeout"
     }, 
     {
       "value": "8388608", 
       "key": "client_oc_target_dirty"
     }, 
     {
       "value": "10", 
       "key": "osd_max_rep"
     }, 
     {
       "value": "600", 
       "key": "filestore_commit_timeout"
     }, 
     {
       "value": "5", 
       "key": "mds_bal_fragment_interval"
     }, 
     {
       "value": "104857600", 
       "key": "filestore_queue_committing_max_bytes"
     }, 
     {
       "value": "false", 
       "key": "osd_preserve_trimmed_log"
     }, 
     {
       "value": "true", 
       "key": "log_flush_on_exit"
     }, 
     {
       "value": "1", 
       "key": "osd_min_rep"
     }, 
     {
       "value": "0.05", 
       "key": "paxos_min_wait"
     }, 
     {
       "value": "1", 
       "key": "num_client"
     }, 
     {
       "value": "false", 
       "key": "rgw_log_nonexistent_bucket"
     }, 
     {
       "value": "/etc/ceph/myceph.mon.gravel1.keyring,/etc/ceph/myceph.keyring,/etc/ceph/keyring,/etc/ceph/keyring.bin", 
       "key": "keyring"
     }, 
     {
       "value": "3600", 
       "key": "osd_snap_trim_thread_timeout"
     }, 
     {
       "value": "false", 
       "key": "filestore_sloppy_crc"
     }, 
     {
       "value": "500", 
       "key": "filestore_wbthrottle_xfs_ios_start_flusher"
     }, 
     {
       "value": "1048576", 
       "key": "mon_sync_max_payload_size"
     }, 
     {
       "value": "20", 
       "key": "osd_peering_wq_batch_size"
     }, 
     {
       "value": "/var/log/ceph/myceph-mon.gravel1.log", 
       "key": "log_file"
     }, 
     {
       "value": "104857600", 
       "key": "mon_client_bytes"
     }, 
     {
       "value": "false", 
       "key": "filestore_journal_writeahead"
     }, 
     {
       "value": "20", 
       "key": "osd_heartbeat_grace"
     }, 
     {
       "value": "1000", 
       "key": "mon_pg_warn_min_pool_objects"
     }, 
     {
       "value": "", 
       "key": "rgw_extended_http_attrs"
     }, 
     {
       "value": "90", 
       "key": "osd_max_write_size"
     }, 
     {
       "value": "1000", 
       "key": "rgw_data_log_changes_size"
     }, 
     {
       "value": "0", 
       "key": "mon_inject_sync_get_chunk_delay"
     }, 
     {
       "value": "", 
       "key": "client_trace"
     }, 
     {
       "value": "true", 
       "key": "filestore_btrfs_snap"
     }, 
     {
       "value": "6", 
       "key": "osd_heartbeat_interval"
     }, 
     {
       "value": ":/0", 
       "key": "cluster_addr"
     }, 
     {
       "value": "1000", 
       "key": "rgw_list_buckets_max_chunk"
     }, 
     {
       "value": "1/1", 
       "key": "crush"
     }, 
     {
       "value": "0", 
       "key": "max_open_files"
     }, 
     {
       "value": "-1", 
       "key": "mds_log_max_events"
     }, 
     {
       "value": "5", 
       "key": "objecter_tick_interval"
     }, 
     {
       "value": "1/5", 
       "key": "mds_migrator"
     }, 
     {
       "value": "0/5", 
       "key": "objclass"
     }, 
     {
       "value": "admin", 
       "key": "rgw_admin_entry"
     }, 
     {
       "value": "20", 
       "key": "mon_pg_warn_min_per_osd"
     }, 
     {
       "value": "3000", 
       "key": "osd_min_pg_log_entries"
     }, 
     {
       "value": "128", 
       "key": "filestore_fd_cache_size"
     }, 
     {
       "value": "false", 
       "key": "mds_bal_frag"
     }, 
     {
       "value": "0.95", 
       "key": "rgw_bucket_quota_soft_threshold"
     }, 
     {
       "value": "false", 
       "key": "osd_compact_leveldb_on_mount"
     }, 
     {
       "value": "0/1", 
       "key": "striper"
     }, 
     {
       "value": "500", 
       "key": "mon_min_osdmap_epochs"
     }, 
     {
       "value": "5", 
       "key": "mon_data_avail_crit"
     }, 
     {
       "value": "10", 
       "key": "filestore_merge_threshold"
     }, 
     {
       "value": "0", 
       "key": "mds_bal_mode"
     }, 
     {
       "value": "4096", 
       "key": "mon_config_key_max_entry_size"
     }, 
     {
       "value": "0.3", 
       "key": "mds_bal_midchunk"
     }, 
     {
       "value": "32", 
       "key": "mon_osd_max_op_age"
     }, 
     {
       "value": "false", 
       "key": "mon_leveldb_paranoid"
     }, 
     {
       "value": "5", 
       "key": "mds_decay_halflife"
     }, 
     {
       "value": "0.9", 
       "key": "osd_failsafe_nearfull_ratio"
     }, 
     {
       "value": "10000", 
       "key": "mon_max_osd"
     }, 
     {
       "value": "false", 
       "key": "osd_debug_verify_stray_on_activate"
     }, 
     {
       "value": ".rgw.root", 
       "key": "rgw_region_root_pool"
     }, 
     {
       "value": "300", 
       "key": "mon_timecheck_interval"
     }, 
     {
       "value": "25000", 
       "key": "mds_bal_split_rd"
     }, 
     {
       "value": "0.5", 
       "key": "osd_scrub_load_threshold"
     }, 
     {
       "value": "10000", 
       "key": "rgw_bucket_quota_cache_size"
     }, 
     {
       "value": "10000", 
       "key": "osd_max_pg_log_entries"
     }, 
     {
       "value": "262144", 
       "key": "mon_slurp_bytes"
     }, 
     {
       "value": "1/5", 
       "key": "javaclient"
     }, 
     {
       "value": "86400", 
       "key": "rgw_swift_token_expiration"
     }, 
     {
       "value": "104857600", 
       "key": "objecter_inflight_op_bytes"
     }, 
     {
       "value": "true", 
       "key": "client_oc"
     }, 
     {
       "value": "60", 
       "key": "filestore_op_thread_timeout"
     }, 
     {
       "value": "false", 
       "key": "log_to_stderr"
     }, 
     {
       "value": "32", 
       "key": "rgw_usage_max_shards"
     }, 
     {
       "value": "524288", 
       "key": "osd_deep_scrub_stride"
     }, 
     {
       "value": "0", 
       "key": "mon_osd_force_trim_to"
     }, 
     {
       "value": "10485760", 
       "key": "journal_max_write_bytes"
     }, 
     {
       "value": "true", 
       "key": "mds_enforce_unique_name"
     }, 
     {
       "value": ".snap", 
       "key": "client_snapdir"
     }, 
     {
       "value": "false", 
       "key": "filestore_journal_trailing"
     }, 
     {
       "value": "15", 
       "key": "mds_beacon_grace"
     }, 
     {
       "value": "false", 
       "key": "client_debug_force_sync_read"
     }, 
     {
       "value": "7300", 
       "key": "ms_bind_port_max"
     }, 
     {
       "value": "0", 
       "key": "client_debug_inject_tick_delay"
     }, 
     {
       "value": "3", 
       "key": "mds_bal_split_bits"
     }, 
     {
       "value": "false", 
       "key": "cephx_require_signatures"
     }, 
     {
       "value": "false", 
       "key": "client_use_random_mds"
     }, 
     {
       "value": "", 
       "key": "key"
     }, 
     {
       "value": "", 
       "key": "rgw_zone"
     }, 
     {
       "value": "-1", 
       "key": "mon_sync_debug_provider"
     }, 
     {
       "value": "/var/run/ceph", 
       "key": "run_dir"
     }, 
     {
       "value": "120", 
       "key": "osd_mon_report_interval_max"
     }, 
     {
       "value": "0/10", 
       "key": "monc"
     }, 
     {
       "value": "1", 
       "key": "osd_recovery_threads"
     }, 
     {
       "value": "true", 
       "key": "journal_block_align"
     }, 
     {
       "value": "false", 
       "key": "lockdep"
     }, 
     {
       "value": "0", 
       "key": "osd_max_attr_size"
     }, 
     {
       "value": "0", 
       "key": "mds_open_remote_link_mode"
     }, 
     {
       "value": "192.168.19.0/24", 
       "key": "cluster_network"
     }, 
     {
       "value": "1/5", 
       "key": "paxos"
     }, 
     {
       "value": "33554432", 
       "key": "journal_queue_max_bytes"
     }, 
     {
       "value": "16", 
       "key": "osd_recovery_op_warn_multiple"
     }, 
     {
       "value": "false", 
       "key": "rgw_s3_auth_use_keystone"
     }, 
     {
       "value": "", 
       "key": "rgw_port"
     }, 
     {
       "value": "0", 
       "key": "osd_leveldb_cache_size"
     }, 
     {
       "value": "0", 
       "key": "ms_inject_delay_probability"
     }, 
     {
       "value": ":/0", 
       "key": "public_addr"
     }, 
     {
       "value": "false", 
       "key": "mds_dump_cache_on_map"
     }, 
     {
       "value": "900", 
       "key": "ms_tcp_read_timeout"
     }, 
     {
       "value": "65536", 
       "key": "mon_leveldb_block_size"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_rename_at"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_import_at"
     }, 
     {
       "value": "false", 
       "key": "osd_recovery_forget_lost_objects"
     }, 
     {
       "value": "30", 
       "key": "osd_target_transaction_size"
     }, 
     {
       "value": "daemon", 
       "key": "mon_cluster_log_to_syslog_facility"
     }, 
     {
       "value": "2", 
       "key": "mon_stat_smooth_intervals"
     }, 
     {
       "value": "false", 
       "key": "mds_debug_subtrees"
     }, 
     {
       "value": "true", 
       "key": "rgw_print_continue"
     }, 
     {
       "value": "true", 
       "key": "mon_force_standby_active"
     }, 
     {
       "value": "default.region", 
       "key": "rgw_default_region_info_oid"
     }, 
     {
       "value": "5", 
       "key": "mon_sync_fs_threshold"
     }, 
     {
       "value": "true", 
       "key": "mon_osd_auto_mark_new_in"
     }, 
     {
       "value": "/", 
       "key": "client_mountpoint"
     }, 
     {
       "value": "1/1", 
       "key": "finisher"
     }, 
     {
       "value": "data_log", 
       "key": "rgw_data_log_obj_prefix"
     }, 
     {
       "value": "1/5", 
       "key": "mds_balancer"
     }, 
     {
       "value": "0.33", 
       "key": "osd_heartbeat_min_healthy_ratio"
     }, 
     {
       "value": "25", 
       "key": "osd_scrub_chunk_max"
     }, 
     {
       "value": "/var/lib/ceph/mds/myceph-gravel1", 
       "key": "mds_data"
     }, 
     {
       "value": "4194304", 
       "key": "rgw_obj_stripe_size"
     }, 
     {
       "value": "0", 
       "key": "osd_pool_default_flags"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_link_at"
     }, 
     {
       "value": "1", 
       "key": "client_tick_interval"
     }, 
     {
       "value": "5", 
       "key": "mon_tick_interval"
     }, 
     {
       "value": "0/5", 
       "key": "rbd"
     }, 
     {
       "value": "1440", 
       "key": "mds_blacklist_interval"
     }, 
     {
       "value": "524288000", 
       "key": "osd_client_message_size_cap"
     }, 
     {
       "value": "", 
       "key": "ms_inject_delay_type"
     }, 
     {
       "value": "false", 
       "key": "clog_to_syslog"
     }, 
     {
       "value": "0", 
       "key": "mds_kill_openc_at"
     }, 
     {
       "value": "4194304", 
       "key": "rgw_get_obj_max_req_size"
     }, 
     {
       "value": "false", 
       "key": "osd_auto_mark_unfound_lost"
     }, 
     {
       "value": "15", 
       "key": "ms_max_backoff"
     }, 
     {
       "value": "myceph", 
       "key": "cluster"
     }, 
     {
       "value": "15", 
       "key": "osd_recovery_max_active"
     }, 
     {
       "value": "true", 
       "key": "rgw_copy_obj_progress"
     }, 
     {
       "value": "false", 
       "key": "rgw_enable_ops_log"
     }, 
     {
       "value": "", 
       "key": "monmap"
     }, 
     {
       "value": "1099511627776", 
       "key": "mds_max_file_size"
     }, 
     {
       "value": "true", 
       "key": "osd_open_classes_on_start"
     }, 
     {
       "value": "", 
       "key": "heartbeat_file"
     }, 
     {
       "value": "false", 
       "key": "mon_osd_auto_mark_in"
     }, 
     {
       "value": "false", 
       "key": "mon_sync_debug"
     }, 
     {
       "value": "false", 
       "key": "mds_standby_replay"
     }, 
     {
       "value": "32", 
       "key": "mon_osd_max_split_count"
     }, 
     {
       "value": "-1", 
       "key": "mds_standby_for_rank"
     }, 
     {
       "value": "500", 
       "key": "osd_map_cache_size"
     }, 
     {
       "value": "5", 
       "key": "heartbeat_interval"
     }, 
     {
       "value": "90", 
       "key": "mds_dir_max_commit_size"
     }, 
     {
       "value": "0.2", 
       "key": "mds_bal_min_start"
     }, 
     {
       "value": "0", 
       "key": "ms_inject_socket_failures"
     }, 
     {
       "value": "900", 
       "key": "rgw_keystone_revocation_interval"
     }, 
     {
       "value": "16777216", 
       "key": "rbd_cache_target_dirty"
     }, 
     {
       "value": "3600", 
       "key": "auth_service_ticket_ttl"
     }, 
     {
       "value": "0", 
       "key": "mds_bal_idle_threshold"
     }, 
     {
       "value": "false", 
       "key": "osd_pool_default_flag_hashpspool"
     }, 
     {
       "value": "0.97", 
       "key": "osd_failsafe_full_ratio"
     }, 
     {
       "value": "5", 
       "key": "client_caps_release_delay"
     }, 
     {
       "value": "-1", 
       "key": "mon_sync_debug_leader"
     }, 
     {
       "value": "false", 
       "key": "ms_bind_ipv6"
     }, 
     {
       "value": "0/5", 
       "key": "client"
     }, 
     {
       "value": "true", 
       "key": "filestore_fail_eio"
     }, 
     {
       "value": "30", 
       "key": "rgw_opstate_ratelimit_sec"
     }, 
     {
       "value": "209715200", 
       "key": "client_oc_size"
     }, 
     {
       "value": "180", 
       "key": "filestore_op_thread_suicide_timeout"
     }, 
     {
       "value": "10", 
       "key": "filestore_max_inline_xattrs_xfs"
     }, 
     {
       "value": "10", 
       "key": "osd_backfill_retry_interval"
     }, 
     {
       "value": "33554432", 
       "key": "mon_leveldb_write_buffer_size"
     }, 
     {
       "value": "10", 
       "key": "mds_bal_target_removal_max"
     }, 
     {
       "value": "0.1", 
       "key": "mds_bal_min_rebalance"
     }, 
     {
       "value": "0", 
       "key": "osd_leveldb_block_size"
     }, 
     {
       "value": "64", 
       "key": "rgw_md_log_max_shards"
     }, 
     {
       "value": "1/5", 
       "key": "rgw"
     }, 
     {
       "value": "false", 
       "key": "fuse_debug"
     }, 
     {
       "value": "8388608", 
       "key": "osd_recovery_max_chunk"
     }, 
     {
       "value": "1/5", 
       "key": "asok"
     }, 
     {
       "value": "", 
       "key": "rgw_ops_log_socket_path"
     }, 
     {
       "value": "false", 
       "key": "rbd_cache_writethrough_until_flush"
     }, 
     {
       "value": "10", 
       "key": "mon_client_ping_interval"
     }, 
     {
       "value": "true", 
       "key": "clog_to_monitors"
     }, 
     {
       "value": "false", 
       "key": "rgw_intent_log_object_name_utc"
     }, 
     {
       "value": "60", 
       "key": "mon_sync_timeout"
     }, 
     {
       "value": "0", 
       "key": "mds_thrash_exports"
     }, 
     {
       "value": "0.3", 
       "key": "mon_osd_min_up_ratio"
     }, 
     {
       "value": "1/5", 
       "key": "mon"
     }, 
     {
       "value": "1000", 
       "key": "client_oc_max_objects"
     }, 
     {
       "value": "30", 
       "key": "osd_mon_heartbeat_interval"
     }, 
     {
       "value": "466b2ff9-970e-44a4-85d1-db0718a0c836", 
       "key": "fsid"
     }, 
     {
       "value": "6", 
       "key": "osd_pgp_bits"
     }, 
     {
       "value": "8388608", 
       "key": "osd_copyfrom_max_chunk"
     }, 
     {
       "value": "5", 
       "key": "mds_scatter_nudge_interval"
     }, 
     {
       "value": "false", 
       "key": "mds_debug_frag"
     }, 
     {
       "value": "0", 
       "key": "mds_log_segment_size"
     }, 
     {
       "value": "0", 
       "key": "mds_skip_ino"
     }, 
     {
       "value": "192.168.18.1,192.168.18.2,192.168.18.3", 
       "key": "mon_host"
     }, 
     {
       "value": "0", 
       "key": "osd_recovery_delay_start"
     }, 
     {
       "value": "0.3", 
       "key": "mon_osd_min_in_ratio"
     }, 
     {
       "value": "0.8", 
       "key": "mds_bal_need_min"
     }, 
     {
       "value": "0", 
       "key": "mds_thrash_fragments"
     }, 
     {
       "value": "4194304", 
       "key": "ms_pq_max_tokens_per_priority"
     }, 
     {
       "value": "1048576", 
       "key": "rgw_copy_obj_progress_every_bytes"
     }, 
     {
       "value": "0/5", 
       "key": "optracker"
     }, 
     {
       "value": "107374182400", 
       "key": "osd_max_object_size"
     }, 
     {
       "value": "0", 
       "key": "mon_sync_requester_kill_at"
     }, 
     {
       "value": "1", 
       "key": "osd_debug_drop_pg_create_duration"
     }, 
     {
       "value": "2", 
       "key": "mds_default_dir_hash"
     }, 
     {
       "value": "false", 
       "key": "mon_leveldb_compression"
     }, 
     {
       "value": "0.85", 
       "key": "osd_backfill_full_ratio"
     }, 
     {
       "value": "5", 
       "key": "osd_recovery_max_single_start"
     }, 
     {
       "value": ".rgw.root", 
       "key": "rgw_zone_root_pool"
     }, 
     {
       "value": "2", 
       "key": "filestore_max_inline_xattrs_other"
     }, 
     {
       "value": "false", 
       "key": "filestore_debug_verify_split"
     }, 
     {
       "value": "5", 
       "key": "filestore_max_sync_interval"
     }, 
     {
       "value": "1000", 
       "key": "mds_bal_merge_rd"
     }, 
     {
       "value": "5", 
       "key": "mds_tick_interval"
     }, 
     {
       "value": "", 
       "key": "rgw_script_uri"
     }, 
     {
       "value": "false", 
       "key": "rbd_cache_block_writes_upfront"
     }, 
     {
       "value": "0/1", 
       "key": "objecter"
     }, 
     {
       "value": "1/5", 
       "key": "heartbeatmap"
     }, 
     {
       "value": "600", 
       "key": "osd_command_thread_timeout"
     }, 
     {
       "value": "true", 
       "key": "journal_dio"
     }, 
     {
       "value": "00000000-0000-0000-0000-000000000000", 
       "key": "osd_uuid"
     }, 
     {
       "value": "6800", 
       "key": "ms_bind_port_min"
     }, 
     {
       "value": "1/3", 
       "key": "journal"
     }, 
     {
       "value": "10", 
       "key": "mon_delta_reset_interval"
     }, 
     {
       "value": "localhost", 
       "key": "host"
     }, 
     {
       "value": "1", 
       "key": "paxos_propose_interval"
     }, 
     {
       "value": "500", 
       "key": "filestore_wbthrottle_btrfs_inodes_start_flusher"
     }, 
     {
       "value": "true", 
       "key": "filestore_btrfs_clone_range"
     }, 
     {
       "value": "auth", 
       "key": "rgw_swift_auth_entry"
     }, 
     {
       "value": "5", 
       "key": "osd_op_log_threshold"
     }, 
     {
       "value": "true", 
       "key": "mon_osd_adjust_heartbeat_grace"
     }, 
     {
       "value": "3", 
       "key": "rbd_default_features"
     }, 
     {
       "value": "1000", 
       "key": "log_max_new"
     }, 
     {
       "value": "250", 
       "key": "paxos_service_trim_min"
     }, 
     {
       "value": "info", 
       "key": "clog_to_syslog_level"
     }, 
     {
       "value": "3", 
       "key": "mds_bal_sample_interval"
     }, 
     {
       "value": "info", 
       "key": "mon_cluster_log_to_syslog_level"
     }, 
     {
       "value": "true", 
       "key": "err_to_stderr"
     }, 
     {
       "value": "false", 
       "key": "filestore_zfs_snap"
     }, 
     {
       "value": "10", 
       "key": "filestore_max_inline_xattrs_btrfs"
     }, 
     {
       "value": "", 
       "key": "osd_rollback_to_cluster_snap"
     }, 
     {
       "value": "true", 
       "key": "rgw_cache_enabled"
     }, 
     {
       "value": "0", 
       "key": "journal_write_header_frequency"
     }, 
     {
       "value": "4194304", 
       "key": "rbd_default_stripe_unit"
     }, 
     {
       "value": "false", 
       "key": "rbd_cache"
     }, 
     {
       "value": "false", 
       "key": "err_to_syslog"
     }, 
     {
       "value": "REMOTE_ADDR", 
       "key": "rgw_remote_addr_param"
     }, 
     {
       "value": "false", 
       "key": "journal_force_aio"
     }, 
     {
       "value": "32", 
       "key": "rgw_gc_max_objs"
     }, 
     {
       "value": "", 
       "key": "mds_standby_for_name"
     }, 
     {
       "value": "25165824", 
       "key": "rbd_cache_max_dirty"
     }, 
     {
       "value": "86400", 
       "key": "osd_scrub_min_interval"
     }, 
     {
       "value": "60", 
       "key": "osd_scrub_thread_timeout"
     }, 
     {
       "value": "0", 
       "key": "filestore_index_retry_probability"
     }, 
     {
       "value": "10", 
       "key": "client_notify_timeout"
     }, 
     {
       "value": "0", 
       "key": "osd_pool_default_crush_rule"
     }, 
     {
       "value": "true", 
       "key": "rgw_enforce_swift_acls"
     }, 
     {
       "value": "false", 
       "key": "rbd_balance_snap_reads"
     }, 
     {
       "value": "/usr/lib/rados-classes", 
       "key": "osd_class_dir"
     }, 
     {
       "value": "1000", 
       "key": "rgw_curl_wait_timeout_ms"
     }, 
     {
       "value": "100", 
       "key": "osd_map_share_max_epochs"
     }, 
     {
       "value": "0/1", 
       "key": "filer"
     }, 
     {
       "value": "10", 
       "key": "mon_slurp_timeout"
     }, 
     {
       "value": "", 
       "key": "rgw_request_uri"
     }, 
     {
       "value": "1000", 
       "key": "mds_client_prealloc_inos"
     }, 
     {
       "value": "false", 
       "key": "rbd_localize_snap_reads"
     }, 
     {
       "value": "10000", 
       "key": "rgw_cache_lru_size"
     }, 
     {
       "value": "gravel1, gravel2, gravel3", 
       "key": "mon_initial_members"
     }, 
     {
       "value": "8", 
       "key": "osd_pool_default_pgp_num"
     }, 
     {
       "value": "10", 
       "key": "mds_bal_interval"
     }, 
     {
       "value": "5", 
       "key": "mds_bal_target_removal_min"
     }, 
     {
       "value": "false", 
       "key": "fuse_use_invalidate_cb"
     }, 
     {
       "value": "0", 
       "key": "mds_shutdown_check"
     }, 
     {
       "value": "false", 
       "key": "mds_debug_scatterstat"
     }, 
     {
       "value": "2", 
       "key": "osd_pool_default_size"
     }, 
     {
       "value": "0", 
       "key": "client_readahead_max_bytes"
     }, 
     {
       "value": "500", 
       "key": "filestore_queue_committing_max_ops"
     }, 
     {
       "value": "1/5", 
       "key": "perfcounter"
     }, 
     {
       "value": "100000", 
       "key": "mds_cache_size"
     }, 
     {
       "value": "419430400", 
       "key": "filestore_wbthrottle_btrfs_bytes_hard_limit"
     }, 
     {
       "value": "", 
       "key": "filestore_dump_file"
     }, 
     {
       "value": "s3, swift, swift_auth, admin", 
       "key": "rgw_enable_apis"
     }, 
     {
       "value": "104857600", 
       "key": "ms_dispatch_throttle_bytes"
     }, 
     {
       "value": "false", 
       "key": "osd_debug_skip_full_check_in_backfill_reservation"
     }, 
     {
       "value": "0.95", 
       "key": "mon_osd_full_ratio"
     }, 
     {
       "value": "64", 
       "key": "osd_backfill_scan_min"
     }, 
     {
       "value": "", 
       "key": "nss_db_path"
     }, 
     {
       "value": "0", 
       "key": "rgw_op_thread_suicide_timeout"
     }, 
     {
       "value": "20", 
       "key": "mds_log_max_expiring"
     }, 
     {
       "value": "", 
       "key": "restapi_log_level"
     }, 
     {
       "value": "10000", 
       "key": "mds_bal_split_size"
     }, 
     {
       "value": "500", 
       "key": "filestore_wbthrottle_btrfs_ios_start_flusher"
     }, 
     {
       "value": "false", 
       "key": "mds_wipe_ino_prealloc"
     }, 
     {
       "value": "true", 
       "key": "mds_log"
     }, 
     {
       "value": "30", 
       "key": "osd_client_watch_timeout"
     }, 
     {
       "value": "65536", 
       "key": "ms_pq_min_cost"
     }, 
     {
       "value": "1", 
       "key": "rgw_usage_max_user_shards"
     }, 
     {
       "value": "50", 
       "key": "filestore_queue_max_ops"
     }, 
     {
       "value": "", 
       "key": "rgw_region"
     }, 
     {
       "value": "-1", 
       "key": "mds_bal_max"
     }, 
     {
       "value": "true", 
       "key": "cephx_sign_messages"
     }, 
     {
       "value": "0.5", 
       "key": "mds_dir_commit_ratio"
     }, 
     {
       "value": "cephx", 
       "key": "auth_service_required"
     }, 
     {
       "value": "3", 
       "key": "mon_client_hunt_interval"
     }, 
     {
       "value": "false", 
       "key": "rgw_resolve_cname"
     }, 
     {
       "value": "63", 
       "key": "osd_client_op_priority"
     }, 
     {
       "value": "45", 
       "key": "mds_reconnect_timeout"
     }, 
     {
       "value": "false", 
       "key": "osd_leveldb_paranoid"
     }, 
     {
       "value": "604800", 
       "key": "osd_deep_scrub_interval"
     }, 
     {
       "value": "10", 
       "key": "osd_heartbeat_min_peers"
     }, 
     {
       "value": "2", 
       "key": "osd_op_threads"
     }, 
     {
       "value": "3", 
       "key": "mon_lease_renew_interval"
     }, 
     {
       "value": "1", 
       "key": "osd_crush_chooseleaf_type"
     }, 
     {
       "value": "true", 
       "key": "mds_use_tmap"
     }, 
     {
       "value": "30", 
       "key": "osd_op_complaint_time"
     }, 
     {
       "value": "128", 
       "key": "rgw_data_log_num_shards"
     }, 
     {
       "value": "false", 
       "key": "ms_die_on_old_message"
     }, 
     {
       "value": "", 
       "key": "auth_supported"
     }, 
     {
       "value": "100", 
       "key": "rgw_thread_pool_size"
     }, 
     {
       "value": "100", 
       "key": "mon_globalid_prealloc"
     }, 
     {
       "value": "false", 
       "key": "filestore_fiemap"
     }
   ]

