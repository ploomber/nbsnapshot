import click

from nbsnapshot import compare


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('-r',
              '--run',
              is_flag=True,
              show_default=True,
              default=False,
              help="Run notebook before comparing.")
def test(path, run):
    """Test a notebook comparing against historical results
    """
    compare.main(path, run=run)
