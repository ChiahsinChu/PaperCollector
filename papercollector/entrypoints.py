import json
import sys
import argparse
from papercollector.main import *


def parse_args():
    """
    PaperCollector commandline options argument parser.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparsers = parser.add_subparsers(title="Valid subcommands",
                                       dest="command")

    # WOS
    parser_wos = subparsers.add_parser(
        'wos', help='Download reference files from Web of Science.')
    parser_wos.add_argument("input", help="Input Json file")

    # DOI
    parser_doi = subparsers.add_parser(
        'doi', help='Extract DOIs from reference files.')
    parser_doi.add_argument("-i", "--input", help="Input Json file")
    parser_doi.add_argument("-s",
                            "--save",
                            help="Specify save path for DOIs.txt.",
                            type=str,
                            default=None)
    parser_doi.add_argument("-e",
                            "--external",
                            help="Specify reference files (support wildcard).",
                            type=str,
                            default=None)
    # PDF
    parser_pdf = subparsers.add_parser('pdf',
                                       help='Download PDF files from Sci-Hub.')
    parser_pdf.add_argument("input", help="Input Json file")
    parser_pdf.add_argument("-e",
                            "--external",
                            help="Specify txt file for DOIs.",
                            type=str,
                            default=None)

    parsed_args = parser.parse_args()
    if parsed_args.command is None:
        parser.print_help()
    return parsed_args


def load_json(json_file):
    with open(json_file, 'r', encoding='utf8') as fp:
        params = json.load(fp)
    return params


def wos(**kwargs):
    params = load_json(kwargs['input'])
    proj = WOS(**params)
    proj.download()


def doi(**kwargs):
    all_refs = kwargs['external']
    params = load_json(kwargs['input'])
    if all_refs is None:
        all_refs = glob.glob(os.path.join(params['wos_path'], 'refs-*'))
    else:
        all_refs = glob.glob(all_refs)
    save_path = kwargs['save']
    if save_path is None:
        save_path = params['wos_path']
    proj = DOIGenerator(all_refs, save_path)
    proj.export_dois()


def pdf(**kwargs):
    params = load_json(kwargs['input'])
    dois = kwargs['external']
    if dois is None:
        if os.path.isfile(os.path.join(params['wos_path'],
                                       'DOIs.txt')) == False:
            doi(**kwargs)
        dois = os.path.join(params['wos_path'], 'DOIs.txt')
    proj = SciHub(dois, **params)
    proj.download()


def main():
    args = parse_args()
    kwargs = vars(args)
    if args.command in ['wos', 'doi', 'pdf']:
        getattr(sys.modules[__name__], args.command)(**kwargs)
    else:
        raise RuntimeError(f"unknown command {args.command}")