from webpie import WPApp, WPHandler
import sys, getopt, os, json

class Handler(WPHandler):
    
    def translate_version(self, product_name, version_or_tag):
        assert isinstance(product_name, str) 
        prod_dir = self.App.ProductRoot + "/" + product_name
        if not os.path.isdir(prod_dir):
            return None, "product not found"
        version_dir = f"{prod_dir}/{version_or_tag}"
        if os.path.islink(version_dir):
            return os.readlink(version_dir).rsplit("/",1)[-1], None
        elif os.path.isdir(version_dir):
            return version_or_tag, None
        else:
            return None, "version not found"
    
    def fetch(self, request, relpath):
        #
        # relpath:
        #   product_name
        #   product_name/tag
        #   product_name/version
        #
        words = relpath.split("/")
        assert len(words) in (1,2)
        product_name = words[0]
        prod_dir = self.App.ProductRoot + "/" + product_name
        version_or_tag = "current"
        if len(words) == 2:
            version_or_tag = words[1]
        version, error = self.translate_version(product_name, version_or_tag)
        if not version:
            return error, 404
        tarname = open(f"{prod_dir}/.product", "r").read().strip()
        tarfile = f"{prod_dir}/{tarname}_{version}.tar"
        def reader(f):
            block = f.read(8*1024)
            while block:
                yield block
                block = f.read(8*1024)
        cache_control = "max-age=3600" if version == version_or_tag else \
            "max-age=0, must-revalidate, no-cache, no-store"
        return reader(open(tarfile, "rb")), {"Cache-Control": cache_control}
        
    def version(self, request, relpath):
        # Translates the tag to version (if needed) and checks if the version exists and returns actual version number
        # if the version does not exist, returns not-found error
        # relpath:
        #   product_name/tag
        #   product_name/version
        #
        words = relpath.split("/")
        assert len(words) == 2
        version, error = self.translate_version(words[0], words[1])
        if not version:
            return error, 404
        return version, "text/plain"
        
    def info(self, request, relpath):
        words = relpath.split("/")
        assert len(words) == 2
        product_name, version_or_tag = words
        version = mtime = None
        version, error = self.translate_version(product_name, version_or_tag)
        if version:
            prod_dir = self.App.ProductRoot + "/" + product_name
            tarname = open(f"{prod_dir}/.product", "r").read().strip()
            tarfile = f"{prod_dir}/{tarname}_{version}.tar"
            try:    
                mtime = os.path.getmtime(tarfile)
                error = None
            except Exception as e:
                mtime = None
                error = str(e)
        return json.dumps({
            "version":  version_or_tag,
            "real_version": version,
            "product": product_name,
            "mtime":    mtime,
            "error":    error
        }), "text/json"

class App(WPApp):
    
    def __init__(self, handler, prod_root):
        WPApp.__init__(self, handler)
        self.ProductRoot = prod_root
        

def create_application(prod_root):
    return App(Handler, prod_root)

application = create_application(".")

Usage = """
python product_server.py <port> <products root>
"""

if __name__ == "__main__":

    opts, args = getopt.getopt(sys.argv[1:], "")
    if len(args) != 2:
        print(Usage)
        sys.exit(2)
    
    port = int(args[0])
    root = args[1]

    create_application(root).run_server(port)
