from nccostorage.bucket import core

# ERRORS
BucketStorageError = core.BucketStorageError
DuplicateBucketError = core.DuplicateBucketError

# Storage Implementation
DictionaryBucketStorage = core.DictionaryBucketStorage

# Fluent API
BucketOperations = core.BucketOperations
Bucket = core.Bucket