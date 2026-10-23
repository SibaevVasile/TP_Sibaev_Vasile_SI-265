from checker import (
    build_url,
    is_https,
    show_response,
    check_site,
    scan_sites,
    check_headers,
    retry_check,
)

print(" PARTEA 1 ")
print("build_url:", build_url("example.com", "login"))
print("build_url (cu slash):", build_url("example.com", "/login"))
print("is_https (True):", is_https("https://example.com"))
print("is_https (False):", is_https("http://example.com"))

print("\n PARTEA 2")
show_response("https://example.com")

print("\n PARTEA 3")
print("check_site bun:", check_site("https://example.com"))
print("check_site rău:", check_site("http://site-care-nu-exista.invalid"))

print("\n PARTEA 4 ")
scan_sites()

print("\n PARTEA 5")
print("check_headers (cu antete):", check_headers("https://httpbin.org/response-headers?X-Frame-Options=DENY&X-Content-Type-Options=nosniff"))
print("check_headers (fără antete de securitate):", check_headers("https://example.com"))

print("\n PARTEA 6 ")
print("retry_check 200:", retry_check("https://httpbin.org/status/200"))
print("retry_check 404:", retry_check("https://httpbin.org/status/404"))
print("retry_check 500:", retry_check("https://httpbin.org/status/500"))
print("retry_check site inexistent:", retry_check("http://this-site-does-not-exist.invalid"))