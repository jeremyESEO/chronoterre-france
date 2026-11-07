"""Exports locaux officiels ; leurs conditions sont documentées jeu par jeu."""
import json
from national.collect import Collector, ROOT, dump


def main():
    sources = json.loads((ROOT / 'config/hazard_layers.json').read_text(encoding='utf-8'))
    c = Collector()
    c.path = ROOT / 'data/raw/hazard_manifest.json'
    c.manifest = json.loads(c.path.read_text(encoding='utf-8')) if c.path.exists() else {
        'version': 2, 'files': {}, 'attempts': [],
    }
    for source in sources:
        data = c.fetch(source['raw'], source['source'], source['url'])
        entry = c.manifest['files'][source['raw']]
        entry.update({k: source[k] for k in ('coverage', 'producer', 'license')})
        for field in ('source_revision', 'license_evidence'):
            if field in source:
                entry[field] = source[field]
        dump(c.path, c.manifest)
        dump(ROOT / source['curated'], data)
    c.fetch('rga_metadata', 'bordeaux_metropole', 'https://datahub.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/ri_alearga_s')
    c.close()


if __name__ == '__main__':
    main()
