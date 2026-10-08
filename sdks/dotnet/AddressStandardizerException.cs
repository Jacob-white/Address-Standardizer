using System.Net;
using System.Net.Http;

namespace AddressStandardizer.Client
{
    /// <summary>
    /// Thrown when the Address Standardizer service returns a non-success HTTP status.
    /// Derives from <see cref="HttpRequestException"/> so existing catch blocks keep working.
    /// </summary>
    public class AddressStandardizerException : HttpRequestException
    {
        /// <summary>Maximum number of response-body characters copied into <see cref="System.Exception.Message"/>.</summary>
        internal const int MaxMessageBodyLength = 512;

#if NET5_0_OR_GREATER
        public AddressStandardizerException(string message, HttpStatusCode statusCode, string responseBody)
            : base(message, null, statusCode)
#else
        public AddressStandardizerException(string message, HttpStatusCode statusCode, string responseBody)
            : base(message)
#endif
        {
            ResponseStatusCode = statusCode;
            ResponseBody = responseBody;
        }

        /// <summary>The HTTP status code returned by the service (available on every target framework).</summary>
        public HttpStatusCode ResponseStatusCode { get; }

        /// <summary>The full response body, which may echo submitted address data.</summary>
        public string ResponseBody { get; }
    }
}
