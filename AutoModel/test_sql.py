#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Function: Auto generate report sql
# Usage: 
#     
# Author: JosingCai
# Email: caijiaoxing@idcos.com
# CreateDate: 2019/06/12
# Update: 

import pymysql
import random
import string

class Database(object):
	"""docstring for Database"""
	def __init__(self):
		#self.db = pymysql.connect(host="10.0.9.33",user="admin",passwd="Yunjikeji#123",db="cloudboot", port=3306,charset = 'utf8')
		self.db = pymysql.connect(host="10.0.3.8",user="root",passwd="Yunjikeji#123",db="cloudboot284_gfsc", port=3306,charset = 'utf8')
		self.cursor = self.db.cursor()

	def get_tables(self):
		cmd = "show tables"
		self.cursor.execute(cmd)
		data = self.cursor.fetchall()
		tables = []
		for item in data:
			item = item[0].encode("utf-8")
			tables.append(item)
		return tables 

	def get_table_comment(self):
		tables = self.get_tables()
		tables_info = []
		for item in tables:
			cmd = "show create table %s" %item
			self.cursor.execute(cmd)
			data = self.cursor.fetchall()
			table_info = {}
			table_info["en_name"] = data[0][0].encode("utf-8")
			tmp_list = data[0][1].split("\n")
			table_info["cn_name"] = tmp_list[-1].split(" ")[-1].split("=")[-1].replace("'", '')
			tables_info.append(table_info)
		return tables_info
		
	def get_table_info(self, name):
		cmd = "show full fields from %s" %name
		self.cursor.execute(cmd)
		data = self.cursor.fetchall()
		seg_infos = []
		for item in data:
			seg_info = {}
			seg_info["cn_name"] = item[8]
			seg_info["en_name"] = item[0]
			seg_infos.append(seg_info)
		return seg_infos

	def get_sys_var_info(self, type_name):
		cmd = 'SELECT value FROM sys_dict where type="%s";'%type_name
		self.cursor.execute(cmd)
		data = self.cursor.fetchall()
		value_list = []
		for item in data:
			value_list.append(item[0])
		return value_list

	def insert_sql(self, cmd):
		self.cursor.execute(cmd)
		self.db.commit()

	def close_handler(self):
		self.cursor.close()
		self.db.close()

class Report(object):
    def __init__(self):
        self.dbhandler = Database(db_info)
        self.filename = "%s/local/SQL/report_sql_%s.sql" %(curPath, today)
        if not os.path.exists(self.filename):
            f = open(self.filename,'w')
            f.close()

    def get_table_list(self, **info):
        return self.dbhandler.get_table_comment()

    def get_table_info(self, **info):
        table_name = info["en_name"][0]
        table_info = self.dbhandler.get_table_info(table_name)
        return table_info

    def post_sql(self, **info):
        cn_name = info["cn_name"][0]
        en_name = info["en_name"][0]
        items = ",".join(info["item"])
        sorts = ",".join(info["sorting"])
        if info["sql_type"][0] == "bar_graph":
            cmd = "select %s,count(1) from %s group by %s;" %(items, en_name, sorts)
            with open(self.filename, 'a+') as f:
               f.write("# %s:%s 柱状图\n" %(cn_name, en_name))
               f.write("%s\n\n" %cmd)

    def get_sql_info(self):
        with open(self.filename) as f:
            content = f.read()
        return content

def insert_sql(number):
    handle = Database()
    for ID in range(number):
        SN = ''.join(random.sample(string.ascii_letters + string.digits, 20))
        cmd_3X0 = "INSERT INTO device (created_at, updated_at, deleted_at, tenant, region_id, sn, manufacturer, model, arch, chassis_type, spec, cpu, memory, nic, logical_disk, physical_disk, raid, oob, bios, fan, power_supply, board, pci, hba, lldp, extra, asset_number, biz_ip, os, hostname, buyer, buy_time, level, application, `usage`, remark, label, oob_ip, oob_user, oob_password, idc_id, server_room_id, server_cabinet_id, begin_unit, height, locator, blade_enclosure_sn, hmc_id, power_status, status, source, creator) VALUES ('2020-03-23 14:57:05', '2020-03-23 14:57:05', null, 'default', 7, '%s', 'Huawei', 'RH2285H V2-12L', 'x86_64', 'blade_server', '12C32G1113G', '{\"items\": [{\"type\": \"Central Processor\", \"cores\": 6, \"flags\": [\"FPU (Floating-point unit on-chip)\", \"VME (Virtual mode extension)\", \"DE (Debugging extension)\", \"PSE (Page size extension)\", \"TSC (Time stamp counter)\", \"MSR (Model specific registers)\", \"PAE (Physical address extension)\", \"MCE (Machine check exception)\", \"CX8 (CMPXCHG8 instruction supported)\", \"APIC (On-chip APIC hardware supported)\", \"SEP (Fast system call)\", \"MTRR (Memory type range registers)\", \"PGE (Page global enable)\", \"MCA (Machine check architecture)\", \"CMOV (Conditional move instruction supported)\", \"PAT (Page attribute table)\", \"PSE-36 (36-bit page size extension)\", \"CLFSH (CLFLUSH instruction supported)\", \"DS (Debug store)\", \"ACPI (ACPI supported)\", \"MMX (MMX technology supported)\", \"FXSR (FXSAVE and FXSTOR instructions supported)\", \"SSE (Streaming SIMD extensions)\", \"SSE2 (Streaming SIMD extensions 2)\", \"SS (Self-snoop)\", \"HTT (Multi-threading)\", \"TM (Thermal monitor supported)\", \"PBE (Pending break enabled)\"], \"model\": \"Intel(R) Xeon(R) CPU E5-2420 @ 1.90GHz\", \"family\": \"Xeon\", \"threads\": 12, \"voltage\": \"0.8 V\", \"l1_cache\": \"0x001B\", \"l2_cache\": \"0x001C\", \"l3_cache\": \"0x001D\", \"max_speed\": \"1900 MHz\", \"manufacturer\": \"Intel(R) Corporation\", \"current_speed\": \"1900 MHz\", \"enabled_cores\": 6, \"socket_designation\": \"CPU01\"}, {\"type\": \"Central Processor\", \"cores\": 6, \"flags\": [\"FPU (Floating-point unit on-chip)\", \"VME (Virtual mode extension)\", \"DE (Debugging extension)\", \"PSE (Page size extension)\", \"TSC (Time stamp counter)\", \"MSR (Model specific registers)\", \"PAE (Physical address extension)\", \"MCE (Machine check exception)\", \"CX8 (CMPXCHG8 instruction supported)\", \"APIC (On-chip APIC hardware supported)\", \"SEP (Fast system call)\", \"MTRR (Memory type range registers)\", \"PGE (Page global enable)\", \"MCA (Machine check architecture)\", \"CMOV (Conditional move instruction supported)\", \"PAT (Page attribute table)\", \"PSE-36 (36-bit page size extension)\", \"CLFSH (CLFLUSH instruction supported)\", \"DS (Debug store)\", \"ACPI (ACPI supported)\", \"MMX (MMX technology supported)\", \"FXSR (FXSAVE and FXSTOR instructions supported)\", \"SSE (Streaming SIMD extensions)\", \"SSE2 (Streaming SIMD extensions 2)\", \"SS (Self-snoop)\", \"HTT (Multi-threading)\", \"TM (Thermal monitor supported)\", \"PBE (Pending break enabled)\"], \"model\": \"Intel(R) Xeon(R) CPU E5-2420 @ 1.90GHz\", \"family\": \"Xeon\", \"threads\": 12, \"voltage\": \"0.8 V\", \"l1_cache\": \"0x0020\", \"l2_cache\": \"0x0021\", \"l3_cache\": \"0x0022\", \"max_speed\": \"1900 MHz\", \"manufacturer\": \"Intel(R) Corporation\", \"current_speed\": \"1900 MHz\", \"enabled_cores\": 6, \"socket_designation\": \"CPU02\"}], \"total_cores\": 12, \"total_threads\": 24, \"total_physicals\": 2}', '{\"items\": [{\"size\": 8589934592, \"type\": \"DDR3\", \"speed\": \"1333 MHz\", \"location\": \"DIMM010\", \"asset_tag\": \"Unknown\", \"part_number\": \"M393B1K70CH0-YH9\", \"manufacturer\": \"Samsung\", \"serial_number\": \"0x33427585\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM011\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 8589934592, \"type\": \"DDR3\", \"speed\": \"1333 MHz\", \"location\": \"DIMM020\", \"asset_tag\": \"Unknown\", \"part_number\": \"M393B1K70CH0-YH9\", \"manufacturer\": \"Samsung\", \"serial_number\": \"0x33427376\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM021\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM030\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM031\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 8589934592, \"type\": \"DDR3\", \"speed\": \"1333 MHz\", \"location\": \"DIMM110\", \"asset_tag\": \"Unknown\", \"part_number\": \"M393B1K70CH0-YH9\", \"manufacturer\": \"Samsung\", \"serial_number\": \"0x33427381\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM111\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 8589934592, \"type\": \"DDR3\", \"speed\": \"1333 MHz\", \"location\": \"DIMM120\", \"asset_tag\": \"Unknown\", \"part_number\": \"M393B1K70CH0-YH9\", \"manufacturer\": \"Samsung\", \"serial_number\": \"0x85A85F03\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM121\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM130\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}, {\"size\": 0, \"type\": \"DDR3\", \"speed\": \"Unknown\", \"location\": \"DIMM131\", \"asset_tag\": \"NO DIMM\", \"part_number\": \"NO DIMM\", \"manufacturer\": \"NO DIMM\", \"serial_number\": \"NO DIMM\", \"configured_voltage\": \"\"}], \"total_size\": 34359738368, \"maximum_size\": 824633720832, \"number_of_devices\": 12, \"number_of_used_devices\": 4}', '{\"items\": [{\"ip\": \"192.168.2.100\", \"mac\": \"04:f9:38:93:3d:3f\", \"link\": \"yes\", \"port\": 0, \"side\": \"inside\", \"type\": \"Ethernet\", \"model\": \"Broadcom Inc. and subsidiaries NetXtreme BCM5719 Gigabit Ethernet PCIe (rev 01)\", \"speed\": \"1Gbit/s\", \"location\": \"eth0\", \"pci_slot\": 0, \"switch_ref\": null, \"bus_address\": \"0000:02:00.0\", \"manufacturer\": \"Broadcom\", \"firmware_version\": \"5719-v1.31 NCSI v1.2.12.0\"}, {\"ip\": \"\", \"mac\": \"04:f9:38:93:3d:40\", \"link\": \"no\", \"port\": 1, \"side\": \"inside\", \"type\": \"Ethernet\", \"model\": \"Broadcom Inc. and subsidiaries NetXtreme BCM5719 Gigabit Ethernet PCIe (rev 01)\", \"speed\": \"1Gbit/s\", \"location\": \"eth1\", \"pci_slot\": 0, \"switch_ref\": null, \"bus_address\": \"0000:02:00.1\", \"manufacturer\": \"Broadcom\", \"firmware_version\": \"5719-v1.31 NCSI v1.2.12.0\"}, {\"ip\": \"\", \"mac\": \"04:f9:38:93:3d:41\", \"link\": \"no\", \"port\": 2, \"side\": \"inside\", \"type\": \"Ethernet\", \"model\": \"Broadcom Inc. and subsidiaries NetXtreme BCM5719 Gigabit Ethernet PCIe (rev 01)\", \"speed\": \"1Gbit/s\", \"location\": \"eth2\", \"pci_slot\": 0, \"switch_ref\": null, \"bus_address\": \"0000:02:00.2\", \"manufacturer\": \"Broadcom\", \"firmware_version\": \"5719-v1.31 NCSI v1.2.12.0\"}, {\"ip\": \"\", \"mac\": \"04:f9:38:93:3d:42\", \"link\": \"no\", \"port\": 3, \"side\": \"inside\", \"type\": \"Ethernet\", \"model\": \"Broadcom Inc. and subsidiaries NetXtreme BCM5719 Gigabit Ethernet PCIe (rev 01)\", \"speed\": \"1Gbit/s\", \"location\": \"eth3\", \"pci_slot\": 0, \"switch_ref\": null, \"bus_address\": \"0000:02:00.3\", \"manufacturer\": \"Broadcom\", \"firmware_version\": \"5719-v1.31 NCSI v1.2.12.0\"}]}', '{\"items\": [{\"name\": \"/dev/sda\", \"size\": \"1113.9 GB, 1195997396992 bytes\"}, {\"name\": \"/dev/sda1\", \"size\": \"0.0 GB, 1048576 bytes\"}, {\"name\": \"/dev/sda2\", \"size\": \"0.2 GB, 268435456 bytes\"}, {\"name\": \"/dev/sda3\", \"size\": \"2.0 GB, 2147483648 bytes\"}, {\"name\": \"/dev/sda4\", \"size\": \"0.0 GB, 1024 bytes\"}, {\"name\": \"/dev/sda5\", \"size\": \"1111.6 GB, 1193578332160 bytes\"}], \"total_size\": 2391992697856}', '{\"items\": [{\"wwn\": \"\", \"size\": 298998443278, \"slot\": \"0\", \"model\": \"HUS156030VLS600 \", \"bus_type\": \"SAS\", \"location\": \"13:0\", \"media_type\": \"HDD\", \"error_count\": 0, \"part_number\": \"\", \"inquiry_data\": \"\", \"manufacturer\": \"\", \"foreign_state\": \"\", \"serial_number\": \"\", \"firmware_state\": \"\", \"transfer_speed\": \"\", \"firmware_version\": \"\"}, {\"wwn\": \"\", \"size\": 298998443278, \"slot\": \"1\", \"model\": \"HUS156030VLS600 \", \"bus_type\": \"SAS\", \"location\": \"13:1\", \"media_type\": \"HDD\", \"error_count\": 0, \"part_number\": \"\", \"inquiry_data\": \"\", \"manufacturer\": \"\", \"foreign_state\": \"\", \"serial_number\": \"\", \"firmware_state\": \"\", \"transfer_speed\": \"\", \"firmware_version\": \"\"}, {\"wwn\": \"\", \"size\": 298998443278, \"slot\": \"2\", \"model\": \"HUS156030VLS600 \", \"bus_type\": \"SAS\", \"location\": \"13:2\", \"media_type\": \"HDD\", \"error_count\": 0, \"part_number\": \"\", \"inquiry_data\": \"\", \"manufacturer\": \"\", \"foreign_state\": \"\", \"serial_number\": \"\", \"firmware_state\": \"\", \"transfer_speed\": \"\", \"firmware_version\": \"\"}, {\"wwn\": \"\", \"size\": 298998443278, \"slot\": \"3\", \"model\": \"HUS156030VLS600 \", \"bus_type\": \"SAS\", \"location\": \"13:3\", \"media_type\": \"HDD\", \"error_count\": 0, \"part_number\": \"\", \"inquiry_data\": \"\", \"manufacturer\": \"\", \"foreign_state\": \"\", \"serial_number\": \"\", \"firmware_state\": \"\", \"transfer_speed\": \"\", \"firmware_version\": \"\"}], \"total_size\": 1195993773112}', '{\"items\": [{\"id\": \"0\", \"mode\": \"\", \"model\": \"SAS2208\", \"pci_address\": \"00:01:00:00\", \"serial_number\": \"\", \"firmware_version\": \"3.190.05-1669\"}]}', '{\"user\": [{\"id\": 2, \"name\": \"yunji\", \"privilege_level\": 4}, {\"id\": 3, \"name\": \"cloudboot1\", \"privilege_level\": 0}, {\"id\": 4, \"name\": \"user\", \"privilege_level\": 2}, {\"id\": 5, \"name\": \"operator\", \"privilege_level\": 3}, {\"id\": 6, \"name\": \"callback\", \"privilege_level\": 2}, {\"id\": 7, \"name\": \"OEMUser\", \"privilege_level\": 0}, {\"id\": 8, \"name\": \"voidint\", \"privilege_level\": 3}, {\"id\": 9, \"name\": \"admin\", \"privilege_level\": 4}, {\"id\": 10, \"name\": \"test\", \"privilege_level\": 4}, {\"id\": 11, \"name\": \"keji\", \"privilege_level\": 0}, {\"id\": 12, \"name\": \"readonly\", \"privilege_level\": 4}], \"network\": {\"ip\": \"192.168.1.164\", \"mac\": \"78:d7:52:93:78:23\", \"ip_src\": \"dhcp\", \"gateway\": \"192.168.1.1\", \"netmask\": \"255.255.0.0\"}, \"firmware\": \"7.31\"}', '{\"manufacturer\": \"Insyde Corp.\", \"release_date\": \"02/11/2018\", \"characteristics\": [\"PCI is supported\", \"BIOS is upgradeable\", \"BIOS shadowing is allowed\", \"Boot from CD is supported\", \"Selectable boot is supported\", \"EDD is supported\", \"Japanese floppy for NEC 9800 1.2 MB is supported (int 13h)\", \"Japanese floppy for Toshiba 1.2 MB is supported (int 13h)\", \"5.25/360 kB floppy services are supported (int 13h)\", \"5.25/1.2 MB floppy services are supported (int 13h)\", \"3.5/720 kB floppy services are supported (int 13h)\", \"3.5/2.88 MB floppy services are supported (int 13h)\", \"8042 keyboard services are supported (int 9h)\", \"CGA/mono video services are supported (int 10h)\", \"ACPI is supported\", \"USB legacy is supported\", \"BIOS boot specification is supported\", \"Targeted content distribution is supported\", \"UEFI is supported\"], \"firmware_version\": \"RMIBV518\"}', '{\"items\": [{\"speed\": \"2400 RPM\", \"location\": \"FAN1 F Speed\"}, {\"speed\": \"2160 RPM\", \"location\": \"FAN1 R Speed\"}, {\"speed\": \"2400 RPM\", \"location\": \"FAN2 F Speed\"}, {\"speed\": \"2040 RPM\", \"location\": \"FAN2 R Speed\"}, {\"speed\": \"2520 RPM\", \"location\": \"FAN3 F Speed\"}, {\"speed\": \"2040 RPM\", \"location\": \"FAN3 R Speed\"}, {\"speed\": \"2520 RPM\", \"location\": \"FAN4 F Speed\"}, {\"speed\": \"2160 RPM\", \"location\": \"FAN4 R Speed\"}]}', '{\"items\": []}', '{\"manufacturer\": \"Huawei Technologies Co., Ltd.\", \"product_name\": \"BC11SRSF1\", \"serial_number\": \"021SKT4ME3000465\", \"onboard_devices\": [], \"firmware_version\": \"V100R002\"}', '{\"items\": [{\"id\": 1, \"type\": \"x4 PCI Express x4\", \"length\": \"Other\", \"pci_device\": null, \"bus_address\": \"0000:00:01.1\", \"designation\": \"PCIE1\", \"current_usage\": \"Available\"}, {\"id\": 2, \"type\": \"x4 PCI Express x4\", \"length\": \"Other\", \"pci_device\": null, \"bus_address\": \"0000:00:1c.4\", \"designation\": \"PCIE2\", \"current_usage\": \"Available\"}, {\"id\": 4, \"type\": \"x16 PCI Express x16\", \"length\": \"Other\", \"pci_device\": null, \"bus_address\": \"0000:80:03.0\", \"designation\": \"PCIE4\", \"current_usage\": \"Available\"}, {\"id\": 5, \"type\": \"x8 PCI Express x8\", \"length\": \"Other\", \"pci_device\": null, \"bus_address\": \"0000:80:01.0\", \"designation\": \"PCIE5\", \"current_usage\": \"Available\"}], \"total_slots\": 4}', null, '{\"lldp\": {\"interface\": {\"eth0\": {\"age\": \"0 day, 00:00:16\", \"rid\": \"1\", \"via\": \"LLDP\", \"port\": {\"id\": {\"type\": \"ifname\", \"value\": \"GigabitEthernet1\/0\/13\"}, \"mfs\": \"10240\", \"descr\": \"GigabitEthernet1\/0\/13 Interface\", \"power\": {\"class\": \"class 0\", \"pairs\": \"signal\", \"source\": \"PSE\", \"enabled\": false, \"priority\": \"critical\", \"allocated\": \"0\", \"requested\": \"0\", \"supported\": false, \"power-type\": \"2\", \"device-type\": \"PSE\", \"paircontrol\": false}, \"auto-negotiation\": {\"current\": \"1000BaseTFD - Four-pair Category 5 UTP, full duplex mode\", \"enabled\": true, \"supported\": true}}, \"vlan\": {\"pvid\": true, \"value\": \"VLAN 0002\", \"vlan-id\": \"2\"}, \"ppvid\": {\"enabled\": false, \"supported\": true}, \"chassis\": {\"iDCOS-H3C-Switch1\": {\"id\": {\"type\": \"mac\", \"value\": \"8c:e6:87:63:01:43\"}, \"ttl\": \"120\", \"descr\": \"H3C Switch S5120-52P-SI Software Version 5.20, Release 1515 Copyright(c) 2004-2015 Hangzhou H3C Tech. Co., Ltd. All rights reserved.\", \"mgmt-ip\": \"192.168.2.254\", \"capability\": [{\"type\": \"Bridge\", \"enabled\": true}, {\"type\": \"Router\", \"enabled\": true}]}}}}}}', null, '', '[\"192.168.2.111\"]', 'ubuntu14.04', 'ubuntu-test', '', '', '1', '', '', '', 'null', '192.168.1.164', 'admin', '7JhjFABmhkzwThULoRCnnPoOuGEtZ4ReK3T2038=', 0, 0, 0, 0, 2, 0, '', 0, 'unknown', 'offline', 'bootos', '6126694f-038f-4049-a964-3ad445e4d47d');"%SN
        cmd_280 = "INSERT INTO device (created_at, updated_at, deleted_at, sn, status, user_id, slave_name, bootos_last_active_time, is_show_in_scan_list, device_id, company, product, model_name, ip, mac, cpu_sum, cpu, memory_sum, memory, disk_sum, disk, disk_slot, nic, nic_device, motherboard, raid, oob, bios, fan, power, hba, pci, switch, lldp, is_vm, extra, raw_product_info, health_check_status, health_check_message, health_check_content, health_check_time, buyer_name, buy_time, expired_time, assign_status, biz_ip, os, host_name, level, location, usite, location_id, `usage`, environment, spec, power_supply_num, supply_power, device_type, config, asset_number, app_user_id, remark) VALUES ('2020-06-03 17:09:23', '2020-06-03 17:10:11', null, '%s', '', '59df5960cd6ac35f53135b31', 'master', '', 'No', 0, 'Dell', '', 'PowerEdge', '', '', 0, '{}', 0, '{}', 0, '{}', '{}', '{}', '', '{}', '{}', '{\"user\": [{\"id\": 0, \"name\": \"admin\", \"password\": \"z4x8TylasH73wW59S5wPqcIzBgfYLYC5\", \"privilege_level\": \"\"}, {\"id\": 0, \"name\": \"root\", \"password\": \"1IlgFwdG5i9MCXpT6lNEOepz1ld+\", \"privilege_level\": \"\"}], \"network\": {\"ip\": \"10.0.10.101\", \"ip_src\": \"static\"}}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', 'No', '{}', null, null, null, null, null, '张三', '2020-04-15', '2020-04-15', 'assigned', null, 'Ubuntu', '', 3, 'A-B-C', '', 1916, '装饰', 'production', '4C', 0, 0, 'server', '1C2G48G', 'test5', '59df5960cd6ac35f53135b31', '测试');" %SN
        print("No.", ID)
        handle.insert_sql(cmd_280)
    handle.close_handler()

if __name__ == '__main__':
   insert_sql(100000)
