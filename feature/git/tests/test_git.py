# pylint: disable=missing-docstring,no-self-use
import shutil
import random
import os.path
import unittest
import subprocess

from dffml.util.tempdir import TempDir
from dffml.util.asynctestcase import AsyncTestCase

from dffml_feature_git.feature.git import Git

def has_git_svn() -> bool:
    '''
    Travis installs git from the maintainers ppa the xenial git-svn does not
    work with, and therefore does not install.
    '''
    try:
        subprocess.check_output(['git', 'svn'], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        if b'clone' in error.output:
            return True
    return False

def mkgitrepo(gitdir):
    subprocess.check_output(['git', 'init'], cwd=gitdir)
    with open(os.path.join(gitdir, 'README.md'), 'w') as handle:
        handle.write('# Hello World')
    subprocess.check_output(['git', 'add', '-A'], cwd=gitdir)
    subprocess.check_output(['git', 'commit', '-m', 'Initial Commit'],
                            cwd=gitdir)

def mksvnrepo(gitdir):
    return

class TestGit(AsyncTestCase):

    async def setUp(self):
        self.tempdir = TempDir()
        await self.tempdir.__aenter__()
        self.gcreated = self.tempdir.mktempdir()
        self.screated = self.tempdir.mktempdir()
        mkgitrepo(self.gcreated)
        mksvnrepo(self.screated)

    async def tearDown(self):
        await self.tempdir.__aexit__(None, None, None)

    async def test_git_clone(self):
        git = Git(self.tempdir)
        self.assertTrue(await git.clone(self.gcreated))
        shutil.rmtree(git.cwd, ignore_errors=True)

    @unittest.skipUnless(has_git_svn() and os.getenv('LONG_TESTS', '') != '',
                         'Long SVN clone')
    async def test_git_clone_svn(self):
        git = Git(self.tempdir)
        self.assertTrue(
                len(await git.clone('https://svn.code.sf.net/p/lame/svn/trunk/lame')))
        shutil.rmtree(git.cwd, ignore_errors=True)

    async def test_no_repo(self):
        git = Git(self.tempdir)
        self.assertFalse(await git.clone(str(random.random())))
        self.assertFalse(os.path.isdir(git.cwd))

    async def test_not_a_git_repo(self):
        git = Git(self.tempdir)
        self.assertFalse(await git.clone('https://example.com'))
        self.assertFalse(os.path.isdir(git.cwd))

    async def test_ls_remote_no_repo(self):
        git = Git(self.tempdir)
        self.assertFalse(await git.ls_remote(str(random.random())))

    async def test_ls_remote(self):
        git = Git(self.tempdir)
        self.assertTrue(await git.ls_remote(self.gcreated))

    @unittest.skipUnless(has_git_svn() and os.getenv('LONG_TESTS', '') != '',
                         'Long SVN ls-remote')
    async def test_ls_remote_svn(self):
        git = Git(self.tempdir)
        self.assertTrue(await git.ls_remote('https://svn.code.sf.net/p/lame/svn/trunk/lame'))

    @unittest.skipUnless(os.getenv('LONG_TESTS', '') != '', 'Hanging test')
    async def test_ls_remote_forever(self):
        '''
        Test case for a repo which hangs for a long time to make sure we git
        ls-remote eventually.
        '''
        git = Git(self.tempdir)
        self.assertFalse(await git.ls_remote('git://java.net/jax-rs-spec~api'))

    async def test_infer_main_branch(self):
        gitdir = self.tempdir.mktempdir()
        subprocess.check_output(['git', 'init'], cwd=gitdir)
        with open(os.path.join(gitdir, 'README.md'), 'w') as handle:
            handle.write('# Hello World')
        subprocess.check_output(['git', 'add', '-A'], cwd=gitdir)
        subprocess.check_output(['git', 'checkout', '-b', 'v2'], cwd=gitdir)
        subprocess.check_output(['git', 'commit', '-m', 'Initial Commit'],
                                cwd=gitdir)
        for src_url, branch in [
                (self.gcreated, 'master'),
                (gitdir, 'v2')]:
            git = Git(self.tempdir)
            with self.subTest(src_url=src_url, branch=branch):
                self.assertTrue(await git.clone(src_url))
                self.assertEqual(git.main_branch, branch)
                shutil.rmtree(git.cwd, ignore_errors=True)
