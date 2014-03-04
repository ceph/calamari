from collections import defaultdict
import hashlib
import json
import os
import uuid
import random
import datetime
from minion_sim.log import log

KB = 1024
GIGS = 1024 * 1024 * 1024
TERABYTES = GIGS * 1024


def md5(raw):
    hasher = hashlib.md5()
    hasher.update(raw)
    return hasher.hexdigest()


DEFAULT_CONFIG = json.loads("""
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
    "mds_dump_cache_on_map": "false",
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
    "run_dir": "/var/run/ceph",
    "rgw_zone": "",
    "mon_sync_debug_provider": "-1",
    "rbd_balance_snap_reads": "false",
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
    "osd_backfill_full_ratio": "0.85",
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
    "filestore_fiemap": "false",
    "mon_osd_max_split_count": "32"
}
""")


DEFAULT_CRUSH = json.loads("""
{ "devices": [
        { "id": 0,
          "name": "osd.0"},
        { "id": 1,
          "name": "osd.1"},
        { "id": 2,
          "name": "osd.2"},
        { "id": 3,
          "name": "osd.3"},
        { "id": 4,
          "name": "osd.4"}],
  "types": [
        { "type_id": 0,
          "name": "osd"},
        { "type_id": 1,
          "name": "host"},
        { "type_id": 2,
          "name": "rack"},
        { "type_id": 3,
          "name": "row"},
        { "type_id": 4,
          "name": "room"},
        { "type_id": 5,
          "name": "datacenter"},
        { "type_id": 6,
          "name": "root"}],
  "buckets": [
        { "id": -1,
          "name": "default",
          "type_id": 6,
          "type_name": "root",
          "weight": 317191,
          "alg": "straw",
          "hash": "rjenkins1",
          "items": [
                { "id": -2,
                  "weight": 197917,
                  "pos": 0},
                { "id": -3,
                  "weight": 59637,
                  "pos": 1},
                { "id": -4,
                  "weight": 59637,
                  "pos": 2}]},
        { "id": -2,
          "name": "gravel1",
          "type_id": 1,
          "type_name": "host",
          "weight": 197917,
          "alg": "straw",
          "hash": "rjenkins1",
          "items": [
                { "id": 0,
                  "weight": 59637,
                  "pos": 0},
                { "id": 3,
                  "weight": 119275,
                  "pos": 1},
                { "id": 4,
                  "weight": 19005,
                  "pos": 2}]},
        { "id": -3,
          "name": "gravel2",
          "type_id": 1,
          "type_name": "host",
          "weight": 59637,
          "alg": "straw",
          "hash": "rjenkins1",
          "items": [
                { "id": 1,
                  "weight": 59637,
                  "pos": 0}]},
        { "id": -4,
          "name": "gravel3",
          "type_id": 1,
          "type_name": "host",
          "weight": 59637,
          "alg": "straw",
          "hash": "rjenkins1",
          "items": [
                { "id": 2,
                  "weight": 59637,
                  "pos": 0}]}],
  "rules": [
        { "rule_id": 0,
          "rule_name": "data",
          "ruleset": 0,
          "type": 1,
          "min_size": 1,
          "max_size": 10,
          "steps": [
                { "op": "take",
                  "item": -1},
                { "op": "chooseleaf_firstn",
                  "num": 0,
                  "type": "host"},
                { "op": "emit"}]},
        { "rule_id": 1,
          "rule_name": "metadata",
          "ruleset": 1,
          "type": 1,
          "min_size": 1,
          "max_size": 10,
          "steps": [
                { "op": "take",
                  "item": -1},
                { "op": "chooseleaf_firstn",
                  "num": 0,
                  "type": "host"},
                { "op": "emit"}]},
        { "rule_id": 2,
          "rule_name": "rbd",
          "ruleset": 2,
          "type": 1,
          "min_size": 1,
          "max_size": 10,
          "steps": [
                { "op": "take",
                  "item": -1},
                { "op": "chooseleaf_firstn",
                  "num": 0,
                  "type": "host"},
                { "op": "emit"}]}],
  "tunables": { "choose_local_tries": 2,
      "choose_local_fallback_tries": 5,
      "choose_total_tries": 19,
      "chooseleaf_descend_once": 0}}
""")


def flatten_dictionary(data, sep='.', prefix=None):
    """Produces iterator of pairs where the first value is
    the joined key names and the second value is the value
    associated with the lowest level key. For example::

      {'a': {'b': 10},
       'c': 20,
       }

    produces::

      [('a.b', 10), ('c', 20)]
    """
    for name, value in sorted(data.items()):
        fullname = sep.join(filter(None, [prefix, name]))
        if isinstance(value, dict):
            for result in flatten_dictionary(value, sep, fullname):
                yield result
        else:
            yield (fullname, value)


def _pool_template(name, pool_id, pg_num):
    """
    Format as in OSD map dump
    """
    return {
        'pool': pool_id,
        'pool_name': name,
        "flags": 0,
        "flags_names": "",
        "type": 1,
        "size": 2,
        "min_size": 1,
        "crush_ruleset": 2,
        "object_hash": 2,
        "pg_num": pg_num,
        "pg_placement_num": pg_num,
        "crash_replay_interval": 0,
        "last_change": "1",
        "auid": 0,
        "snap_mode": "selfmanaged",
        "snap_seq": 0,
        "snap_epoch": 0,
        "pool_snaps": {},
        "removed_snaps": "[]",
        "quota_max_bytes": 0,
        "quota_max_objects": 0,
        "tiers": [],
        "tier_of": -1,
        "read_tier": -1,
        "write_tier": -1,
        "cache_mode": "none",
        "properties": []
    }


def pseudorandom_subset(possible_values, n_select, selector):
    result = []
    for i in range(0, n_select):
        result.append(possible_values[hash(selector + i.__str__()) % len(possible_values)])
    return result


def get_hostname(fqdn):
    return fqdn.split(".")[0]


class CephClusterState(object):
    def __init__(self, filename=None):
        self._filename = filename
        if self._filename is not None and os.path.exists(self._filename):
            self.load()
        else:
            self.fsid = None
            self.name = None

            self._service_locations = {
                "osd": {},
                "mon": {}
            }
            self._host_services = defaultdict(list)
            self._objects = dict()
            self._pg_stats = {}
            self._osd_stats = {}

    def load(self):
        assert self._filename is not None

        data = json.load(open(self._filename))
        self._service_locations = data['service_locations']
        self._host_services = defaultdict(list, data['host_services'])
        self.fsid = data['fsid']
        self.name = data['name']

        # The public objects (health, OSD map, brief PG info, etc)
        # This is the subset the RADOS interface that Calamari needs
        self._objects = data['objects']

        # The hidden state (in real ceph this would be accessible but
        # we hide it so that we can use simplified versions of things
        # like the PG map)
        self._osd_stats = data['osd_stats']
        self._pg_stats = data['pg_stats']

    def save(self):
        assert self._filename is not None

        dump = {
            'fsid': self.fsid,
            'name': self.name,
            'objects': self._objects,
            'osd_stats': self._osd_stats,
            'pg_stats': self._pg_stats,
            'service_locations': self._service_locations,
            'host_services': self._host_services
        }
        json.dump(dump, open(self._filename, 'w'))

    def create(self, fqdns, mon_count=3, osds_per_host=4, osd_overlap=False, osd_size=2 * TERABYTES):
        """
        Generate initial state for a cluster
        """
        log.info("Creating ceph_cluster")

        self.fsid = uuid.uuid4().__str__()
        self.name = 'ceph_fake'

        mon_hosts = fqdns[0:mon_count]
        if osd_overlap:
            osd_hosts = fqdns[mon_count:]
        else:
            osd_hosts = fqdns

        osd_id = 0
        for fqdn in osd_hosts:
            for i in range(0, osds_per_host):
                self._service_locations["osd"][osd_id] = fqdn
                self._host_services[fqdn].append({
                    'type': 'osd',
                    'id': osd_id,
                    'fsid': self.fsid
                })
                osd_id += 1

        for fqdn in mon_hosts:
            mon_id = get_hostname(fqdn)
            self._service_locations["mon"][mon_id] = fqdn
            self._host_services[fqdn].append({
                "type": "mon",
                "id": mon_id,
                'fsid': self.fsid
            })

        # Mon health check output
        # =======================
        self._objects['health'] = {
            'detail': [],
            'health': {
                'health_services': [],
            },
            'overall_status': "HEALTH_OK",
            'summary': [],
            'timechecks': {}
        }

        # Cluster config settings
        # =======================
        self._objects['config'] = DEFAULT_CONFIG

        # OSD map
        # =======
        osd_count = len(osd_hosts) * osds_per_host

        self._objects['osd_map'] = {
            'fsid': self.fsid,
            'max_osd': osd_count,
            'epoch': 1,
            'osds': [],
            'pools': [],
            'crush': DEFAULT_CRUSH
        }

        for i in range(0, osd_count):
            # TODO populate public_addr and cluster_addr from imagined
            # interface addresses of servers
            osd_id = i
            self._objects['osd_map']['osds'].append({
                'osd': osd_id,
                'uuid': uuid.uuid4().__str__(),
                'up': 1,
                'in': 1,
                'last_clean_begin': 0,
                'last_clean_end': 0,
                'up_from': 0,
                'up_thru': 0,
                'down_at': 0,
                'lost_at': 0,
                'public_addr': "",
                'cluster_addr': "",
                'heartbeat_back_addr': "",
                'heartbeat_front_addr': "",
                "state": ["exists", "up"]
            })
            self._osd_stats[osd_id] = {
                'total_bytes': osd_size
            }

        for i, pool in enumerate(['data', 'metadata', 'rbd']):
            # TODO these should actually have a different crush ruleset etc each
            self._objects['osd_map']['pools'].append(_pool_template(pool, i, 64))

        tree = {
            "nodes": [
                {
                    "id": -1,
                    "name": "default",
                    "type": "root",
                    "type_id": 6,
                    "children": []
                }
            ]
        }

        host_tree_id = -2
        for fqdn, services in self._host_services.items():
            # Entries for OSDs on this host
            for s in services:
                if s['type'] != 'osd':
                    continue

                tree['nodes'].append({
                    "id": s['id'],
                    "name": "osd.%s" % s['id'],
                    "exists": 1,
                    "type": "osd",
                    "type_id": 0,
                    "status": "up",
                    "reweight": 1.0,
                    "crush_weight": 1.0,
                    "depth": 2
                })

            # Entry for the host itself
            tree['nodes'].append({
                "id": host_tree_id,
                "name": get_hostname(fqdn),
                "type": "host",
                "type_id": 1,
                "children": [
                    s['id'] for s in services if s['type'] == 'osd'
                ]
            })
            tree['nodes'][0]['children'].append(host_tree_id)
            host_tree_id -= 1

        self._objects['osd_map']['tree'] = tree

        # Mon status
        # ==========
        self._objects['mon_map'] = {
            'epoch': 0,
            'fsid': self.fsid,
            'modified': datetime.datetime.now().isoformat(),
            'created': datetime.datetime.now().isoformat(),
            'mons': [

            ],
            'quorum': []
        }
        for i, mon_fqdn in enumerate(mon_hosts):
            # TODO: populate addr
            self._objects['mon_map']['mons'].append({
                'rank': i,
                'name': get_hostname(mon_fqdn),
                'addr': ""
            })
            self._objects['mon_map']['quorum'].append(i)
        self._objects['mon_status'] = {
            "election_epoch": 77,
            "rank": 0,  # IRL the rank here is an arbitrary one from within quorum
            "state": "leader",
            "monmap": self._objects['mon_map'],
            "quorum": [m['rank'] for m in self._objects['mon_map']['mons']]
        }

        self._objects['mds_map'] = {
            "max_mds": 1,
            "in": [],
            "up": {},
            "info": {}
        }

        # PG map
        # ======
        self._objects['pg_brief'] = []
        # Don't maintain a full PG map but do maintain a version counter.
        self._objects['pg_map'] = {"version": 1}
        for pool in self._objects['osd_map']['pools']:
            n_replicas = pool['size']
            for pg_num in range(pool['pg_num']):
                pg_id = "%s.%s" % (pool['pool'], pg_num)
                osds = pseudorandom_subset(range(0, osd_count), n_replicas, pg_id)
                self._objects['pg_brief'].append({
                    'pgid': pg_id,
                    'state': 'active+clean',
                    'up': osds,
                    'acting': osds
                })

                self._pg_stats[pg_id] = {
                    'num_objects': 0,
                    'num_bytes': 0,
                    'num_bytes_wr': 0,
                    'num_bytes_rd': 0
                }


class CephCluster(CephClusterState):
    """
    An approximate simulation of a Ceph cluster.

    Use for driving test/demo environments.
    """

    def get_services(self, fqdn):
        return self._host_services[fqdn]

    def get_heartbeat(self, fsid):
        return {
            'name': self.name,
            'fsid': self.fsid,
            'versions': {
                'health': md5(json.dumps(self._objects['health'])),
                'mds_map': 1,
                'mon_map': 1,
                'mon_status': self._objects['mon_status']['election_epoch'],
                'osd_map': self._objects['osd_map']['epoch'],
                'osd_tree': 1,
                'pg_map': self._objects['pg_map']['version'],
                'pg_brief': md5(json.dumps(self._objects['pg_brief'])),
                'config': md5(json.dumps(self._objects['config']))
            }
        }

    def get_cluster_object(self, cluster_name, sync_type, since):
        data = self._objects[sync_type]
        if sync_type == 'osd_map':
            version = data['epoch']
        elif sync_type == 'mon_status':
            version = data['election_epoch']
        elif sync_type == 'health' or sync_type == 'pg_brief' or sync_type == 'config':
            version = md5(json.dumps(data))
        else:
            version = 1

        return {
            'fsid': self.fsid,
            'version': version,
            'type': sync_type,
            'data': data
        }

    def _pg_id_to_osds(self, pg_id):
        # TODO: respect the pool's replication policy
        replicas = 2

        possible_osd_ids = [o['osd'] for o in self._objects['osd_map']['osds'] if o['in']]

        return pseudorandom_subset(possible_osd_ids, replicas, pg_id)

    def _object_id_to_pg(self, pool_id, object_id):
        pg_num = 0
        for p in self._objects['osd_map']['pools']:
            if p['pool'] == pool_id:
                pg_num = p['pg_num']
        if pg_num is 0:
            raise RuntimeError("Pool %s not found" % pool_id)

        return "{0}.{1}".format(pool_id, hash(object_id.__str__()) % pg_num)

    def rados_write(self, pool_id, n, size):
        # Pick a random base ID
        base_id = random.randint(0, 10000)

        for i in range(0, n):
            object_id = base_id + i
            pg_id = self._object_id_to_pg(pool_id, object_id)

            # Record the object's existence
            self._pg_stats[pg_id]['num_objects'] += 1
            self._pg_stats[pg_id]['num_bytes'] += size
            self._pg_stats[pg_id]['num_bytes_wr'] += size
            # NB assuming all other usage stats are calculated from
            # PG stats

    def set_osd_state(self, osd_id, up=None, osd_in=None):
        log.debug("set_osd_state: '%s' %s %s %s" % (osd_id, osd_id.__class__, up, osd_in))
        # Update OSD map
        dirty = False
        osd = [o for o in self._objects['osd_map']['osds'] if o['osd'] == osd_id][0]
        if up is not None and osd['up'] != up:
            log.debug("Mark OSD %s up=%s" % (osd_id, up))
            osd['up'] = up
            dirty = True
        if osd_in is not None and osd['in'] != osd_in:
            log.debug("Mark OSD %s in=%s" % (osd_id, osd_in))
            osd['in'] = osd_in
            dirty = True

        if not dirty:
            return

        log.debug("Advancing OSD map")
        self._objects['osd_map']['epoch'] += 1

        self._pg_monitor()
        self._update_health()

    def set_osd_weight(self, osd_id, weight):
        node = [n for n in self._objects['osd_map']['tree']['nodes'] if n['id'] == osd_id][0]
        node['reweight'] = weight
        self._objects['osd_map']['epoch'] += 1

        self._pg_monitor()
        self._update_health()

    def _create_pgs(self, pool_id, new_ids):
        pool = [p for p in self._objects['osd_map']['pools'] if p['pool'] == pool_id][0]
        for i in new_ids:
            pg_id = "%s.%s" % (pool['pool'], i)
            log.debug("_create_pgs created pg %s" % pg_id)
            osds = pseudorandom_subset(range(0, len(self._objects['osd_map']['osds'])),
                                       pool['size'], pg_id)
            self._objects['pg_brief'].append({
                'pgid': pg_id,
                'state': 'creating',
                'up': osds,
                'acting': osds
            })
        self._objects['pg_map']['version'] += 1

    def pool_create(self, pool_name, pg_num):
        log.info("pool_create: %s/%s" % (pool_name, pg_num))
        if pool_name in [p['pool_name'] for p in self._objects['osd_map']['pools']]:
            log.error("Pool %s already exists" % pool_name)
            return

        new_id = max([p['pool'] for p in self._objects['osd_map']['pools']]) + 1
        log.info("pool_create assigned %s=%s" % (pool_name, new_id))

        self._objects['osd_map']['pools'].append(
            _pool_template(pool_name, new_id, pg_num)
        )
        self._objects['osd_map']['epoch'] += 1
        self._create_pgs(new_id, range(0, pg_num))

    def pool_update(self, pool_name, var, val):
        log.info("pool_update %s %s %s" % (pool_name, var, val))
        pool = [p for p in self._objects['osd_map']['pools'] if p['pool_name'] == pool_name][0]

        if var == 'pg_num':
            log.debug("pool_update creating pgs %s->%s" % (
                pool['pg_num'], val
            ))
            # Growing a pool, creating PGs
            new_pg_count = val - pool['pg_num']
            osd_count = min(pool['pg_num'], len(self._objects['osd_map']['osds']))
            if new_pg_count > osd_count * int(self._objects['config']['mon_osd_max_split_count']):
                raise RuntimeError("Exceeded mon_osd_max_split_count")
            self._create_pgs(pool['pool'], range(pool['pg_num'], val))

        if var == 'pgp_num':
            # On the way in it's called pgp_num, on the way out it's called pg_placement_num
            var = 'pg_placement_num'

        if pool[var] != val:
            pool[var] = val
            self._objects['osd_map']['epoch'] += 1

    def pool_delete(self, pool_name):
        if pool_name in [p['pool_name'] for p in self._objects['osd_map']['pools']]:
            self._objects['osd_map']['pools'] = [p for p in self._objects['osd_map']['pools'] if
                                                 p['pool_name'] != pool_name]
            self._objects['osd_map']['epoch'] += 1

    def _pg_monitor(self, recovery_credits=0, creation_credits=0):
        """
        Crude facimile of the PG monitor.  For each PG, based on its
        current state and the state of its OSDs, update it: usually do
        nothing, maybe mark it stale, maybe remap it.
        """

        osds = dict([(osd['osd'], osd) for osd in self._objects['osd_map']['osds']])

        changes = False
        for pg in self._objects['pg_brief']:
            states = set(pg['state'].split('+'))
            primary_osd_id = pg['acting'][0]
            # Call a PG is stale if its primary OSD is down
            if osds[primary_osd_id]['in'] == 1 and osds[primary_osd_id]['up'] == 0:
                states.add('stale')
            else:
                states.discard('stale')

            # Call a PG active if any of its OSDs are in
            if any([osds[i]['in'] == 1 for i in pg['acting']]):
                states.add('active')
            else:
                states.discard('active')

            # Remap a PG if any of its OSDs are out
            if any([osds[i]['in'] == 0 for i in pg['acting']]):
                states.add('remapped')
                osd_ids = self._pg_id_to_osds(pg['pgid'])
                pg['up'] = osd_ids
                pg['acting'] = osd_ids

            # Call a PG clean if its not remapped and all its OSDs are in
            if all([osds[i]['in'] == 1 for i in pg['acting']]) and not 'remapped' in states:
                states.add('clean')
            else:
                states.discard('clean')

            if recovery_credits > 0 and 'remapped' in states:
                states.discard('remapped')
                recovery_credits -= 1
                log.debug("Recovered PG %s" % pg['pgid'])

            if creation_credits > 0 and 'creating' in states:
                states.discard('creating')
                creation_credits -= 1
                log.debug("Completed creation PG %s" % pg['pgid'])

            new_state = "+".join(sorted(list(states)))
            if pg['state'] != new_state:
                log.debug("New PG state %s: %s" % (pg['pgid'], new_state))
                changes = True
                pg['state'] = new_state

        if changes:
            self._objects['pg_map']['version'] += 1
            self._update_health()

    def advance(self, t):
        RECOVERIES_PER_SECOND = 1
        CREATIONS_PER_SECOND = 10
        self._pg_monitor(t * RECOVERIES_PER_SECOND, t * CREATIONS_PER_SECOND)
        self._update_health()

    def _update_health(self):
        """
        Update the 'health' object based on the cluster maps
        """

        old_health = self._objects['health']['overall_status']
        if any([pg['state'] != 'active+clean' for pg in self._objects['pg_brief']]):
            health = "HEALTH_WARN"
            self._objects['health']['summary'] = [{
                'severity': "HEALTH_WARN",
                'summary': "Unclean PGs"
            }]
        else:
            health = "HEALTH_OK"

        if old_health != health:
            self._objects['health']['overall_status'] = health
            log.debug("update_health: %s->%s" % (old_health, health))

    def update_rates(self):
        pass
        # Reduce the PG stats across affected objects:
        # - The bytes per sec and IOPS per sec for the OSDs
        # - The bytes per sec and IOPs per sec for the pool
        # - The bytes per sec and packets per sec for the public
        #   and cluster network interfaces
        # - The bytes per sec and IOPs for the data and journal
        #   drives for the OSDs

    def get_stats(self, fqdn):
        stats = dict()
        hostname = fqdn.split('.')[0]

        # Server stats
        # =============
        cpu_count = 2
        cpu_stat_names = ['guest', 'guest_nice', 'idle', 'iowait', 'irq', 'nice', 'softirq', 'steal', 'system', 'user']
        cpu_stats = defaultdict(dict)

        for k in cpu_stat_names:
            cpu_stats['total'][k] = 0
        for cpu in range(cpu_count):
            # Junk stats to generate load on carbon/graphite
            for k in cpu_stat_names:
                v = random.random()
                cpu_stats["cpu{0}".format(cpu)][k] = random.random()
                cpu_stats['total'][k] += v

        stats.update(flatten_dictionary(cpu_stats, prefix="servers.{0}.cpu".format(hostname)))

        # Network stats
        # =============
        interfaces = ['em1', 'p1p1', 'p1p2']
        net_stats = defaultdict(dict)
        for interface in interfaces:
            for k in ['rx_byte', 'rx_compressed', 'rx_drop', 'rx_errors', 'rx_fifo', 'rx_frame', 'rx_multicast',
                      'rx_packets', 'tx_byte', 'tx_compressed', 'tx_drop', 'tx_errors', 'tx_fifo', 'tx_frame',
                      'tx_multicast', 'tx_packets']:
                net_stats[interface][k] = random.random()
        stats.update(flatten_dictionary(net_stats, prefix="servers.{0}.network".format(hostname)))

        # Service stats
        # =============

        # Cluster stats
        # =============
        leader_name = None
        if self._objects['mon_map']['quorum']:
            leader_id = self._objects['mon_map']['quorum'][0]
            leader = [m for m in self._objects['mon_map']['mons'] if m['rank'] == leader_id][0]
            leader_name = leader['name']

        if get_hostname(fqdn) == leader_name:
            pool_stats = defaultdict(lambda: dict(
                bytes_used=0,
                kb_used=0,
                objects=0
            ))

            for pg_id, pg_stats in self._pg_stats.items():
                pool_id = int(pg_id.split(".")[0])
                pool_stats[pool_id]['bytes_used'] += pg_stats['num_bytes']
                pool_stats[pool_id]['objects'] += pg_stats['num_objects']

            for s in pool_stats.values():
                s['kb_used'] = s['bytes_used'] / KB

            total_used = 0
            for pool_id, pstats in pool_stats.items():
                total_used += pstats['bytes_used']
                for k, v in pstats.items():
                    stats["ceph.cluster.{0}.pool.{1}.{2}".format(self.name, pool_id, k)] = v

            total_space = sum([o['total_bytes'] for o in self._osd_stats.values()])

            # These stats are given in kB
            df_stats = {
                'total_space': total_space / 1024,
                'total_used': total_used / 1024,
                'total_avail': (total_space - total_used) / 1024
            }
            for k, v in df_stats.items():
                stats["ceph.cluster.{0}.df.{1}".format(self.name, k)] = v

        return stats.items()

    def get_service_fqdns(self, service_type):
        """
        Given a service type (mon or osd), return an iterable
        of FQDNs of servers where that type of service is running.
        """
        return self._service_locations[service_type].values()

    def get_name(self):
        """
        Getter for the benefit of XMLRPC clients who can't access properties
        """
        return self.name
