# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: bootable/recovery/update_verifier/care_map.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='bootable/recovery/update_verifier/care_map.proto',
  package='recovery_update_verifier',
  syntax='proto3',
  serialized_options=_b('H\003'),
  serialized_pb=_b('\n0bootable/recovery/update_verifier/care_map.proto\x12\x18recovery_update_verifier\"\x9e\x01\n\x07\x43\x61reMap\x12\x43\n\npartitions\x18\x01 \x03(\x0b\x32/.recovery_update_verifier.CareMap.PartitionInfo\x1aN\n\rPartitionInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06ranges\x18\x02 \x01(\t\x12\n\n\x02id\x18\x03 \x01(\t\x12\x13\n\x0b\x66ingerprint\x18\x04 \x01(\tB\x02H\x03\x62\x06proto3')
)




_CAREMAP_PARTITIONINFO = _descriptor.Descriptor(
  name='PartitionInfo',
  full_name='recovery_update_verifier.CareMap.PartitionInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='recovery_update_verifier.CareMap.PartitionInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ranges', full_name='recovery_update_verifier.CareMap.PartitionInfo.ranges', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='id', full_name='recovery_update_verifier.CareMap.PartitionInfo.id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fingerprint', full_name='recovery_update_verifier.CareMap.PartitionInfo.fingerprint', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=159,
  serialized_end=237,
)

_CAREMAP = _descriptor.Descriptor(
  name='CareMap',
  full_name='recovery_update_verifier.CareMap',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='partitions', full_name='recovery_update_verifier.CareMap.partitions', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_CAREMAP_PARTITIONINFO, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=79,
  serialized_end=237,
)

_CAREMAP_PARTITIONINFO.containing_type = _CAREMAP
_CAREMAP.fields_by_name['partitions'].message_type = _CAREMAP_PARTITIONINFO
DESCRIPTOR.message_types_by_name['CareMap'] = _CAREMAP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CareMap = _reflection.GeneratedProtocolMessageType('CareMap', (_message.Message,), {

  'PartitionInfo' : _reflection.GeneratedProtocolMessageType('PartitionInfo', (_message.Message,), {
    'DESCRIPTOR' : _CAREMAP_PARTITIONINFO,
    '__module__' : 'bootable.recovery.update_verifier.care_map_pb2'
    # @@protoc_insertion_point(class_scope:recovery_update_verifier.CareMap.PartitionInfo)
    })
  ,
  'DESCRIPTOR' : _CAREMAP,
  '__module__' : 'bootable.recovery.update_verifier.care_map_pb2'
  # @@protoc_insertion_point(class_scope:recovery_update_verifier.CareMap)
  })
_sym_db.RegisterMessage(CareMap)
_sym_db.RegisterMessage(CareMap.PartitionInfo)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
