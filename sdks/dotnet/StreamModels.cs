using System;

namespace AddressStandardizer.Client
{
    /// <summary>A record of an NDJSON batch stream that the server could not standardize.</summary>
    public sealed class RecordError
    {
        public RecordError(int index, string message)
        {
            Index = index;
            Message = message;
        }

        /// <summary>Position of the failed record in the request.</summary>
        public int Index { get; }

        public string Message { get; }
    }

    /// <summary>One result of a batch stream. Exactly one of <see cref="Address"/> and <see cref="Error"/> is set.</summary>
    public sealed class StreamRecord
    {
        public StandardizedAddress? Address { get; set; }

        public RecordError? Error { get; set; }
    }

    /// <summary>Thrown by <c>StreamBatchAsync</c> when the server reports that a record could not be standardized.</summary>
    public sealed class AddressStandardizerRecordException : Exception
    {
        public AddressStandardizerRecordException(int index, string message)
            : base($"Record {index} could not be standardized: {message}")
        {
            Index = index;
        }

        public int Index { get; }
    }
}
