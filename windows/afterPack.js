// Zet het Radio Curious-icoon en de programmagegevens in Playlist XXL.exe (zonder Wine)
const fs = require('fs'), path = require('path');
module.exports = async ctx => {
  const ResEdit = await import('resedit');
  const R = ResEdit.default || ResEdit;
  const exe = path.join(ctx.appOutDir, `${ctx.packager.appInfo.productFilename}.exe`);
  const data = fs.readFileSync(exe);
  const pe = R.NtExecutable.from(data, { ignoreCert: true });
  const res = R.NtExecutableResource.from(pe);
  const ico = R.Data.IconFile.from(fs.readFileSync(path.join(__dirname, 'build', 'icon.ico')));
  R.Resource.IconGroupEntry.replaceIconsForResource(res.entries, 1, 1033, ico.icons.map(i => i.data));
  const vi = R.Resource.VersionInfo.fromEntries(res.entries)[0];
  vi.setStringValues({ lang: 1033, codepage: 1200 }, {
    ProductName: 'CURIOUS XXL', FileDescription: 'CURIOUS XXL — Radio Curious',
    CompanyName: 'Han Koopman · Radio Curious', LegalCopyright: '© 2026 Han Koopman. Alle rechten voorbehouden. Niet verspreiden zonder toestemming.', OriginalFilename: 'CURIOUS XXL.exe', InternalName: 'CURIOUS XXL'
  });
  vi.setFileVersion(1, 1, 0, 0, 1033); vi.setProductVersion(1, 1, 0, 0, 1033);
  vi.outputToResourceEntries(res.entries);
  res.outputResource(pe);
  fs.writeFileSync(exe, Buffer.from(pe.generate()));
  console.log('icoon gezet in', exe);
};
