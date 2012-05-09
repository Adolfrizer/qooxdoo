/* ************************************************************************

   qooxdoo - the new era of web development

   http://qooxdoo.org

   Copyright:
     2012 1&1 Internet AG, Germany, http://www.1und1.de

   License:
     LGPL: http://www.gnu.org/licenses/lgpl.html
     EPL: http://www.eclipse.org/org/documents/epl-v10.php
     See the LICENSE file in the project's top-level directory for details.

   Authors:
     * Tino Butz (tbtz)

************************************************************************ */

qx.Class.define("qx.test.mobile.container.Navigation",
{
  extend : qx.test.mobile.MobileTestCase,

  members :
  {
    testCreate : function()
    {
      var container = new qx.ui.mobile.container.Navigation();
      this.getRoot().add(container);
      container.destroy();
    },
    
    
    testAdd : function()
    {
      var container = new qx.ui.mobile.container.Navigation();
      var page = new qx.ui.mobile.page.Page();
      this.getRoot().add(container);
      this.assertFalse(container.getContent().hasChildren());      
      container.add(page);
      this.assertTrue(container.getContent().hasChildren());
      page.destroy();
      container.destroy();
    },
    
    
    testRemove : function()
    {
      var container = new qx.ui.mobile.container.Navigation();
      var page = new qx.ui.mobile.page.Page();
      this.getRoot().add(container);
      this.assertFalse(container.getContent().hasChildren());      
      container.add(page);
      this.assertTrue(container.getContent().hasChildren());
      container.remove(page);
      this.assertFalse(container.getContent().hasChildren());
      page.destroy();
      container.destroy();
    }
  }

});
